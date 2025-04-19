import os
import sqlite3
import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import io
from PIL import Image, ImageTk


class Database:
    def __init__(self, db_name="SUPERVISOR.DB"):
        self.db_name = db_name
        self.create_tables()

    def connect(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        return conn, cursor

    def create_tables(self):
        conn, cursor = self.connect()

        try:
            # Criar tabelas se não existirem
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS vigilantes (
                id_vigilante INTEGER PRIMARY KEY AUTOINCREMENT,
                nome VARCHAR(100) NOT NULL,
                matricula VARCHAR(20) UNIQUE NOT NULL,
                cnv VARCHAR(20) UNIQUE,
                ativo INTEGER DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS supervisores (
                id_supervisor INTEGER PRIMARY KEY AUTOINCREMENT,
                nome VARCHAR(100) NOT NULL,
                matricula VARCHAR(20) UNIQUE NOT NULL,
                email VARCHAR(100),
                ativo INTEGER DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS postos (
                id_posto INTEGER PRIMARY KEY AUTOINCREMENT,
                nome VARCHAR(100) NOT NULL,
                endereco TEXT,
                ativo INTEGER DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS inspecoes (
                id_inspecao INTEGER PRIMARY KEY AUTOINCREMENT,
                id_supervisor INTEGER NOT NULL,
                id_vigilante INTEGER NOT NULL,
                id_posto INTEGER NOT NULL,
                data_inspecao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                observacoes TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_supervisor) REFERENCES supervisores(id_supervisor),
                FOREIGN KEY (id_vigilante) REFERENCES vigilantes(id_vigilante),
                FOREIGN KEY (id_posto) REFERENCES postos(id_posto)
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS apontamentos (
                id_apontamento INTEGER PRIMARY KEY AUTOINCREMENT,
                id_inspecao INTEGER NOT NULL,
                epi_conforme INTEGER,
                epi_observacao TEXT,
                posto_conforme INTEGER,
                posto_observacao TEXT,
                armamento_conforme INTEGER,
                armamento_observacao TEXT,
                documentacao_conforme INTEGER,
                documentacao_observacao TEXT,
                saude_psicofisica_conforme INTEGER,
                saude_observacao TEXT,
                procedimentos_conforme INTEGER,
                procedimentos_observacao TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_inspecao) REFERENCES inspecoes(id_inspecao)
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS nao_conformidades (
                id_nao_conformidade INTEGER PRIMARY KEY AUTOINCREMENT,
                id_apontamento INTEGER NOT NULL,
                descricao TEXT NOT NULL,
                acao_corretiva TEXT,
                prazo_acoes DATE,
                status VARCHAR(20) DEFAULT 'Pendente' CHECK (status IN ('Pendente', 'Em Andamento', 'Concluído')),
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_apontamento) REFERENCES apontamentos(id_apontamento)
            )
            ''')

            conn.commit()
        finally:
            conn.close()

    def fetch_all(self, query, params=None):
        conn, cursor = self.connect()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Buscar todos os resultados antes de fechar a conexão
            results = cursor.fetchall()
            return results
        except Exception as e:
            print(f"Erro na execução da query: {e}")
            return []
        finally:
            conn.close()

    def fetch_one(self, query, params=None):
        conn, cursor = self.connect()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Buscar um resultado antes de fechar a conexão
            result = cursor.fetchone()
            return result
        except Exception as e:
            print(f"Erro na execução da query: {e}")
            return None
        finally:
            conn.close()

    def execute_query(self, query, params=None):
        conn, cursor = self.connect()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            conn.commit()
            return True
        except Exception as e:
            print(f"Erro na execução da query: {e}")
            return False
        finally:
            conn.close()

    def insert(self, table, data):
        conn, cursor = self.connect()
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

            cursor.execute(query, tuple(data.values()))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Erro ao inserir dados: {e}")
            return None
        finally:
            conn.close()

    def update(self, table, data, condition):
        conn, cursor = self.connect()
        try:
            set_clause = ', '.join([f"{key} = ?" for key in data])
            query = f"UPDATE {table} SET {set_clause} WHERE {condition}"

            cursor.execute(query, tuple(data.values()))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Erro ao atualizar dados: {e}")
            return 0
        finally:
            conn.close()

    def delete(self, table, condition):
        conn, cursor = self.connect()
        try:
            query = f"DELETE FROM {table} WHERE {condition}"

            cursor.execute(query)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Erro ao excluir dados: {e}")
            return 0
        finally:
            conn.close()

    def import_csv(self, table, file_path):
        conn, cursor = self.connect()
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    columns = ', '.join(row.keys())
                    placeholders = ', '.join(['?' for _ in row])
                    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                    cursor.execute(query, tuple(row.values()))
                conn.commit()
                return True
        except Exception as e:
            print(f"Erro ao importar CSV: {e}")
            return False
        finally:
            conn.close()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Supervisão de Vigilantes")
        self.geometry("1200x700")
        self.db = Database()

        # Carregar e redimensionar o logo
        try:
            self.logo_image = Image.open("logo.jpg")
            self.logo_image = self.logo_image.resize((150, 150), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(self.logo_image)
            self.logo_label = tk.Label(self, image=self.logo_photo)
            self.logo_label.pack(side=tk.TOP, pady=10)
        except Exception as e:
            print(f"Erro ao carregar logo: {e}")

        # Criar notebook para abas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Criar abas
        self.tab_vigilantes = ttk.Frame(self.notebook)
        self.tab_supervisores = ttk.Frame(self.notebook)
        self.tab_postos = ttk.Frame(self.notebook)
        self.tab_inspecoes = ttk.Frame(self.notebook)
        self.tab_apontamentos = ttk.Frame(self.notebook)
        self.tab_nao_conformidades = ttk.Frame(self.notebook)
        self.tab_relatorios = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_vigilantes, text="Vigilantes")
        self.notebook.add(self.tab_supervisores, text="Supervisores")
        self.notebook.add(self.tab_postos, text="Postos")
        self.notebook.add(self.tab_inspecoes, text="Inspeções")
        self.notebook.add(self.tab_apontamentos, text="Apontamentos")
        self.notebook.add(self.tab_nao_conformidades, text="Não Conformidades")
        self.notebook.add(self.tab_relatorios, text="Relatórios")

        # Configurar cada aba
        self.setup_vigilantes_tab()
        self.setup_supervisores_tab()
        self.setup_postos_tab()
        self.setup_inspecoes_tab()
        self.setup_apontamentos_tab()
        self.setup_nao_conformidades_tab()
        self.setup_relatorios_tab()

        # Estilo
        self.style = ttk.Style()
        self.style.configure("Treeview", font=('Arial', 10))
        self.style.configure("Treeview.Heading", font=('Arial', 11, 'bold'))
        self.style.configure("TButton", font=('Arial', 10))
        self.style.configure("TLabel", font=('Arial', 10))
        self.style.configure("TEntry", font=('Arial', 10))

    def setup_vigilantes_tab(self):
        self.setup_crud_tab(
            self.tab_vigilantes,
            "vigilantes",
            ["ID", "Nome", "Matrícula", "CNV", "Ativo", "Criado em"],
            [
                {"name": "nome", "type": "entry", "label": "Nome"},
                {"name": "matricula", "type": "entry", "label": "Matrícula"},
                {"name": "cnv", "type": "entry", "label": "CNV"},
                {"name": "ativo", "type": "combobox", "label": "Ativo", "values": ["1", "0"]}
            ]
        )

    def setup_supervisores_tab(self):
        self.setup_crud_tab(
            self.tab_supervisores,
            "supervisores",
            ["ID", "Nome", "Matrícula", "Email", "Ativo", "Criado em"],
            [
                {"name": "nome", "type": "entry", "label": "Nome"},
                {"name": "matricula", "type": "entry", "label": "Matrícula"},
                {"name": "email", "type": "entry", "label": "Email"},
                {"name": "ativo", "type": "combobox", "label": "Ativo", "values": ["1", "0"]}
            ]
        )

    def setup_postos_tab(self):
        self.setup_crud_tab(
            self.tab_postos,
            "postos",
            ["ID", "Nome", "Endereço", "Ativo", "Criado em"],
            [
                {"name": "nome", "type": "entry", "label": "Nome"},
                {"name": "endereco", "type": "entry", "label": "Endereço"},
                {"name": "ativo", "type": "combobox", "label": "Ativo", "values": ["1", "0"]}
            ]
        )

    def setup_inspecoes_tab(self):
        # Obter supervisores, vigilantes e postos para os comboboxes
        supervisores = self.db.fetch_all("SELECT id_supervisor, nome FROM supervisores")
        vigilantes = self.db.fetch_all("SELECT id_vigilante, nome FROM vigilantes")
        postos = self.db.fetch_all("SELECT id_posto, nome FROM postos")

        self.setup_crud_tab(
            self.tab_inspecoes,
            "inspecoes",
            ["ID", "Supervisor", "Vigilante", "Posto", "Data Inspeção", "Observações", "Criado em"],
            [
                {"name": "id_supervisor", "type": "combobox", "label": "Supervisor",
                 "values": [str(s[0]) for s in supervisores], "display": [s[1] for s in supervisores]},
                {"name": "id_vigilante", "type": "combobox", "label": "Vigilante",
                 "values": [str(v[0]) for v in vigilantes], "display": [v[1] for v in vigilantes]},
                {"name": "id_posto", "type": "combobox", "label": "Posto",
                 "values": [str(p[0]) for p in postos], "display": [p[1] for p in postos]},
                {"name": "data_inspecao", "type": "entry", "label": "Data Inspeção (YYYY-MM-DD HH:MM:SS)"},
                {"name": "observacoes", "type": "text", "label": "Observações"}
            ],
            join_query="""
            SELECT i.id_inspecao, s.nome, v.nome, p.nome, i.data_inspecao, i.observacoes, i.criado_em
            FROM inspecoes i
            JOIN supervisores s ON i.id_supervisor = s.id_supervisor
            JOIN vigilantes v ON i.id_vigilante = v.id_vigilante
            JOIN postos p ON i.id_posto = p.id_posto
            """
        )

    def setup_apontamentos_tab(self):
        # Obter inspeções para o combobox
        inspecoes = self.db.fetch_all("SELECT id_inspecao FROM inspecoes")

        self.setup_crud_tab(
            self.tab_apontamentos,
            "apontamentos",
            ["ID", "Inspeção", "EPI Conforme", "Obs. EPI", "Posto Conforme", "Obs. Posto",
             "Armamento Conforme", "Obs. Armamento", "Doc. Conforme", "Obs. Doc.",
             "Saúde Conforme", "Obs. Saúde", "Proc. Conforme", "Obs. Proc.", "Criado em"],
            [
                {"name": "id_inspecao", "type": "combobox", "label": "Inspeção",
                 "values": [str(i[0]) for i in inspecoes]},
                {"name": "epi_conforme", "type": "combobox", "label": "EPI Conforme", "values": ["1", "0"]},
                {"name": "epi_observacao", "type": "entry", "label": "Observação EPI"},
                {"name": "posto_conforme", "type": "combobox", "label": "Posto Conforme", "values": ["1", "0"]},
                {"name": "posto_observacao", "type": "entry", "label": "Observação Posto"},
                {"name": "armamento_conforme", "type": "combobox", "label": "Armamento Conforme", "values": ["1", "0"]},
                {"name": "armamento_observacao", "type": "entry", "label": "Observação Armamento"},
                {"name": "documentacao_conforme", "type": "combobox", "label": "Documentação Conforme",
                 "values": ["1", "0"]},
                {"name": "documentacao_observacao", "type": "entry", "label": "Observação Documentação"},
                {"name": "saude_psicofisica_conforme", "type": "combobox", "label": "Saúde Conforme",
                 "values": ["1", "0"]},
                {"name": "saude_observacao", "type": "entry", "label": "Observação Saúde"},
                {"name": "procedimentos_conforme", "type": "combobox", "label": "Procedimentos Conforme",
                 "values": ["1", "0"]},
                {"name": "procedimentos_observacao", "type": "entry", "label": "Observação Procedimentos"}
            ]
        )

    def setup_nao_conformidades_tab(self):
        # Obter apontamentos para o combobox
        apontamentos = self.db.fetch_all("SELECT id_apontamento FROM apontamentos")

        self.setup_crud_tab(
            self.tab_nao_conformidades,
            "nao_conformidades",
            ["ID", "Apontamento", "Descrição", "Ação Corretiva", "Prazo", "Status", "Criado em"],
            [
                {"name": "id_apontamento", "type": "combobox", "label": "Apontamento",
                 "values": [str(a[0]) for a in apontamentos]},
                {"name": "descricao", "type": "text", "label": "Descrição"},
                {"name": "acao_corretiva", "type": "text", "label": "Ação Corretiva"},
                {"name": "prazo_acoes", "type": "entry", "label": "Prazo (YYYY-MM-DD)"},
                {"name": "status", "type": "combobox", "label": "Status",
                 "values": ["Pendente", "Em Andamento", "Concluído"]}
            ]
        )

    def setup_relatorios_tab(self):
        frame = ttk.Frame(self.tab_relatorios)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Opções de relatório
        ttk.Label(frame, text="Selecione o tipo de relatório:").grid(row=0, column=0, sticky=tk.W, pady=5)

        self.relatorio_var = tk.StringVar()
        relatorio_combo = ttk.Combobox(frame, textvariable=self.relatorio_var, state="readonly")
        relatorio_combo["values"] = [
            "Conformidade por Posto",
            "Não Conformidades por Status",
            "Inspeções por Supervisor",
            "Vigilantes Ativos/Inativos",
            "Postos Ativos/Inativos"
        ]
        relatorio_combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        relatorio_combo.current(0)

        # Botões
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="Gerar Gráfico", command=self.gerar_grafico).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Exportar PDF", command=self.exportar_pdf).pack(side=tk.LEFT, padx=5)

        # Frame para o gráfico
        self.grafico_frame = ttk.Frame(frame)
        self.grafico_frame.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, pady=10)

        # Configurar expansão
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)

    def setup_crud_tab(self, tab, table_name, columns, fields, join_query=None):
        # Frame principal
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame superior para botões
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=5)

        # Botões CRUD
        ttk.Button(top_frame, text="Adicionar", command=lambda: self.show_form(table_name, fields)).pack(side=tk.LEFT,
                                                                                                         padx=5)
        ttk.Button(top_frame, text="Editar", command=lambda: self.edit_selected(table_name, fields)).pack(side=tk.LEFT,
                                                                                                          padx=5)
        ttk.Button(top_frame, text="Excluir", command=lambda: self.delete_selected(table_name)).pack(side=tk.LEFT,
                                                                                                     padx=5)
        ttk.Button(top_frame, text="Atualizar", command=lambda: self.refresh_table(table_name, join_query)).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Importar CSV", command=lambda: self.import_csv(table_name)).pack(side=tk.LEFT,
                                                                                                     padx=5)

        # Frame para a tabela
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Scrollbars
        y_scrollbar = ttk.Scrollbar(table_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        x_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview (tabela)
        tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                            yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)

        # Configurar colunas
        for i, col in enumerate(columns):
            tree.heading(i, text=col)
            tree.column(i, width=100, minwidth=50)

        tree.pack(fill=tk.BOTH, expand=True)

        # Configurar scrollbars
        y_scrollbar.config(command=tree.yview)
        x_scrollbar.config(command=tree.xview)

        # Armazenar referência à tabela
        setattr(self, f"tree_{table_name}", tree)

        # Carregar dados
        self.refresh_table(table_name, join_query)

    def refresh_table(self, table_name, join_query=None):
        tree = getattr(self, f"tree_{table_name}")

        # Limpar tabela
        for item in tree.get_children():
            tree.delete(item)

        # Carregar dados
        if join_query:
            rows = self.db.fetch_all(join_query)
        else:
            rows = self.db.fetch_all(f"SELECT * FROM {table_name}")

        # Preencher tabela
        for row in rows:
            tree.insert("", tk.END, values=row)

    def show_form(self, table_name, fields, values=None):
        # Criar janela de formulário
        form_window = tk.Toplevel(self)
        form_window.title(f"{'Editar' if values else 'Adicionar'} {table_name.capitalize()}")
        form_window.geometry("500x600")
        form_window.grab_set()  # Modal

        # Frame para campos
        fields_frame = ttk.Frame(form_window, padding=10)
        fields_frame.pack(fill=tk.BOTH, expand=True)

        # Dicionário para armazenar widgets de entrada
        entries = {}

        # Criar campos
        for i, field in enumerate(fields):
            ttk.Label(fields_frame, text=field["label"]).grid(row=i, column=0, sticky=tk.W, pady=5)

            if field["type"] == "entry":
                entry = ttk.Entry(fields_frame, width=40)
                entry.grid(row=i, column=1, sticky=tk.W, pady=5)
                if values and i + 1 < len(values):
                    entry.insert(0, values[i + 1] or "")
                entries[field["name"]] = entry

            elif field["type"] == "text":
                text = tk.Text(fields_frame, width=40, height=4)
                text.grid(row=i, column=1, sticky=tk.W, pady=5)
                if values and i + 1 < len(values):
                    text.insert("1.0", values[i + 1] or "")
                entries[field["name"]] = text

            elif field["type"] == "combobox":
                if "display" in field:
                    # Criar dicionário para mapear display -> value
                    display_map = {field["display"][j]: field["values"][j] for j in range(len(field["values"]))}
                    combo_values = field["display"]
                else:
                    display_map = None
                    combo_values = field["values"]

                combo = ttk.Combobox(fields_frame, values=combo_values, state="readonly", width=38)
                combo.grid(row=i, column=1, sticky=tk.W, pady=5)

                if values and i + 1 < len(values):
                    if display_map:
                        # Encontrar o display correspondente ao valor
                        for display, value in display_map.items():
                            if value == str(values[i + 1]):
                                combo.set(display)
                                break
                    else:
                        combo.set(values[i + 1])

                # Armazenar o combobox e o mapa de display
                entries[field["name"]] = (combo, display_map)

        # Frame para botões
        buttons_frame = ttk.Frame(form_window, padding=10)
        buttons_frame.pack(fill=tk.X)

        # Botões
        ttk.Button(buttons_frame, text="Cancelar", command=form_window.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Salvar",
                   command=lambda: self.save_form(table_name, fields, entries, values[0] if values else None,
                                                  form_window)).pack(side=tk.RIGHT, padx=5)

    def save_form(self, table_name, fields, entries, id_value, form_window):
        # Coletar dados do formulário
        data = {}
        for field in fields:
            if field["type"] == "entry":
                data[field["name"]] = entries[field["name"]].get()
            elif field["type"] == "text":
                data[field["name"]] = entries[field["name"]].get("1.0", tk.END).strip()
            elif field["type"] == "combobox":
                combo, display_map = entries[field["name"]]
                if display_map:
                    # Converter display para value
                    data[field["name"]] = display_map.get(combo.get(), "")
                else:
                    data[field["name"]] = combo.get()

        # Validar dados
        for field in fields:
            if field["name"] in data and not data[field["name"]] and field["name"] not in ["cnv", "email",
                                                                                           "observacoes"]:
                messagebox.showerror("Erro", f"O campo {field['label']} é obrigatório.")
                return

        try:
            # Inserir ou atualizar no banco de dados
            if id_value:
                id_field = f"id_{table_name[:-1]}" if table_name.endswith("s") else f"id_{table_name}"
                self.db.update(table_name, data, f"{id_field} = {id_value}")
            else:
                self.db.insert(table_name, data)

            # Atualizar tabela
            self.refresh_table(table_name)

            # Fechar formulário
            form_window.destroy()

            messagebox.showinfo("Sucesso",
                                f"{table_name.capitalize()} {'atualizado' if id_value else 'adicionado'} com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")

    def edit_selected(self, table_name, fields):
        tree = getattr(self, f"tree_{table_name}")
        selected = tree.selection()

        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item para editar.")
            return

        # Obter valores do item selecionado
        values = tree.item(selected[0], "values")

        # Mostrar formulário com valores preenchidos
        self.show_form(table_name, fields, values)

    def delete_selected(self, table_name):
        tree = getattr(self, f"tree_{table_name}")
        selected = tree.selection()

        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item para excluir.")
            return

        # Confirmar exclusão
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este item?"):
            return

        # Obter ID do item selecionado
        values = tree.item(selected[0], "values")
        id_value = values[0]

        try:
            # Excluir do banco de dados
            id_field = f"id_{table_name[:-1]}" if table_name.endswith("s") else f"id_{table_name}"
            self.db.delete(table_name, f"{id_field} = {id_value}")

            # Atualizar tabela
            self.refresh_table(table_name)

            messagebox.showinfo("Sucesso", f"{table_name.capitalize()} excluído com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir: {str(e)}")

    def import_csv(self, table_name):
        # Abrir diálogo para selecionar arquivo
        file_path = filedialog.askopenfilename(
            title="Selecione o arquivo CSV",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if not file_path:
            return

        try:
            # Importar CSV
            if self.db.import_csv(table_name, file_path):
                # Atualizar tabela
                self.refresh_table(table_name)
                messagebox.showinfo("Sucesso", f"Dados importados com sucesso para {table_name}!")
            else:
                messagebox.showerror("Erro", "Falha ao importar dados.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao importar CSV: {str(e)}")

    def gerar_grafico(self):
        tipo_relatorio = self.relatorio_var.get()

        # Limpar frame do gráfico
        for widget in self.grafico_frame.winfo_children():
            widget.destroy()

        # Criar figura e canvas
        fig, ax = plt.subplots(figsize=(8, 6))

        if tipo_relatorio == "Conformidade por Posto":
            # Consulta para obter dados de conformidade por posto
            query = """
            SELECT p.nome, 
                   SUM(a.epi_conforme) as epi, 
                   SUM(a.posto_conforme) as posto,
                   SUM(a.armamento_conforme) as armamento,
                   SUM(a.documentacao_conforme) as doc,
                   SUM(a.saude_psicofisica_conforme) as saude,
                   SUM(a.procedimentos_conforme) as proc,
                   COUNT(a.id_apontamento) as total
            FROM apontamentos a
            JOIN inspecoes i ON a.id_inspecao = i.id_inspecao
            JOIN postos p ON i.id_posto = p.id_posto
            GROUP BY p.nome
            """
            dados = self.db.fetch_all(query)

            if not dados:
                messagebox.showinfo("Aviso", "Não há dados suficientes para gerar este relatório.")
                return

            # Preparar dados para o gráfico
            postos = [d[0] for d in dados]
            conformidade = [(d[1] + d[2] + d[3] + d[4] + d[5] + d[6]) / (d[7] * 6) * 100 if d[7] > 0 else 0 for d in
                            dados]

            # Criar gráfico de barras
            ax.bar(postos, conformidade, color='skyblue')
            ax.set_xlabel('Postos')
            ax.set_ylabel('% Conformidade')
            ax.set_title('Conformidade por Posto')
            ax.set_ylim(0, 100)
            plt.xticks(rotation=45, ha='right')

        elif tipo_relatorio == "Não Conformidades por Status":
            # Consulta para obter dados de não conformidades por status
            query = """
            SELECT status, COUNT(*) as total
            FROM nao_conformidades
            GROUP BY status
            """
            dados = self.db.fetch_all(query)

            if not dados:
                messagebox.showinfo("Aviso", "Não há dados suficientes para gerar este relatório.")
                return

            # Preparar dados para o gráfico
            status = [d[0] for d in dados]
            totais = [d[1] for d in dados]

            # Criar gráfico de pizza
            ax.pie(totais, labels=status, autopct='%1.1f%%', startangle=90, colors=['red', 'orange', 'green'])
            ax.set_title('Não Conformidades por Status')
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle

        elif tipo_relatorio == "Inspeções por Supervisor":
            # Consulta para obter dados de inspeções por supervisor
            query = """
            SELECT s.nome, COUNT(i.id_inspecao) as total
            FROM inspecoes i
            JOIN supervisores s ON i.id_supervisor = s.id_supervisor
            GROUP BY s.nome
            """
            dados = self.db.fetch_all(query)

            if not dados:
                messagebox.showinfo("Aviso", "Não há dados suficientes para gerar este relatório.")
                return

            # Preparar dados para o gráfico
            supervisores = [d[0] for d in dados]
            totais = [d[1] for d in dados]

            # Criar gráfico de barras
            ax.bar(supervisores, totais, color='lightgreen')
            ax.set_xlabel('Supervisores')
            ax.set_ylabel('Número de Inspeções')
            ax.set_title('Inspeções por Supervisor')
            plt.xticks(rotation=45, ha='right')

        elif tipo_relatorio == "Vigilantes Ativos/Inativos":
            # Consulta para obter dados de vigilantes ativos/inativos
            query = """
            SELECT ativo, COUNT(*) as total
            FROM vigilantes
            GROUP BY ativo
            """
            dados = self.db.fetch_all(query)

            if not dados:
                messagebox.showinfo("Aviso", "Não há dados suficientes para gerar este relatório.")
                return

            # Preparar dados para o gráfico
            status = ["Ativo" if d[0] == 1 else "Inativo" for d in dados]
            totais = [d[1] for d in dados]

            # Criar gráfico de pizza
            ax.pie(totais, labels=status, autopct='%1.1f%%', startangle=90, colors=['green', 'red'])
            ax.set_title('Vigilantes Ativos/Inativos')
            ax.axis('equal')

        elif tipo_relatorio == "Postos Ativos/Inativos":
            # Consulta para obter dados de postos ativos/inativos
            query = """
            SELECT ativo, COUNT(*) as total
            FROM postos
            GROUP BY ativo
            """
            dados = self.db.fetch_all(query)

            if not dados:
                messagebox.showinfo("Aviso", "Não há dados suficientes para gerar este relatório.")
                return

            # Preparar dados para o gráfico
            status = ["Ativo" if d[0] == 1 else "Inativo" for d in dados]
            totais = [d[1] for d in dados]

            # Criar gráfico de pizza
            ax.pie(totais, labels=status, autopct='%1.1f%%', startangle=90, colors=['green', 'red'])
            ax.set_title('Postos Ativos/Inativos')
            ax.axis('equal')

        # Ajustar layout
        plt.tight_layout()

        # Criar canvas Tkinter para exibir o gráfico
        canvas = FigureCanvasTkAgg(fig, master=self.grafico_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def exportar_pdf(self):
        tipo_relatorio = self.relatorio_var.get()

        # Abrir diálogo para salvar arquivo
        file_path = filedialog.asksaveasfilename(
            title="Salvar Relatório PDF",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )

        if not file_path:
            return

        try:
            # Criar documento PDF
            doc = SimpleDocTemplate(file_path, pagesize=landscape(letter))
            elements = []

            # Estilos
            styles = getSampleStyleSheet()
            title_style = styles["Heading1"]
            subtitle_style = styles["Heading2"]
            normal_style = styles["Normal"]

            # Título
            elements.append(Paragraph(f"Relatório: {tipo_relatorio}", title_style))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
            elements.append(Spacer(1, 24))

            # Dados para o relatório
            if tipo_relatorio == "Conformidade por Posto":
                query = """
                SELECT p.nome, 
                       SUM(a.epi_conforme) as epi, 
                       SUM(a.posto_conforme) as posto,
                       SUM(a.armamento_conforme) as armamento,
                       SUM(a.documentacao_conforme) as doc,
                       SUM(a.saude_psicofisica_conforme) as saude,
                       SUM(a.procedimentos_conforme) as proc,
                       COUNT(a.id_apontamento) as total
                FROM apontamentos a
                JOIN inspecoes i ON a.id_inspecao = i.id_inspecao
                JOIN postos p ON i.id_posto = p.id_posto
                GROUP BY p.nome
                """
                dados = self.db.fetch_all(query)

                if not dados:
                    messagebox.showinfo("Aviso", "Não há dados suficientes para gerar este relatório.")
                    return

                # Cabeçalho da tabela
                table_data = [
                    ["Posto", "EPI", "Posto", "Armamento", "Documentação", "Saúde", "Procedimentos", "% Conformidade"]]

                # Dados da tabela
                for d in dados:
                    conformidade = (d[1] + d[2] + d[3] + d[4] + d[5] + d[6]) / (d[7] * 6) * 100 if d[7] > 0 else 0
                    table_data.append([
                        d[0],
                        f"{d[1]}/{d[7]}",
                        f"{d[2]}/{d[7]}",
                        f"{d[3]}/{d[7]}",
                        f"{d[4]}/{d[7]}",
                        f"{d[5]}/{d[7]}",
                        f"{d[6]}/{d[7]}",
                        f"{conformidade:.1f}%"
                    ])

            elif tipo_relatorio == "Não Conformidades por Status":
                query = """
                SELECT nc.id_nao_conformidade, a.id_apontamento, nc.descricao, nc.acao_corretiva, 
                       nc.prazo_acoes, nc.status, i.data_inspecao, p.nome as posto, v.nome as vigilante
                FROM nao_conformidades nc
                JOIN apontamentos a ON nc.id_apontamento = a.id_apontamento
                JOIN inspecoes i ON a.id_inspecao = i.id_inspecao
                JOIN postos p ON i.id_posto = p.id_posto
                JOIN vigilantes v ON i.id_vigilante = v.id_vigilante
                ORDER BY nc.status, nc.prazo_acoes
                """
                dados = self.db.fetch_all(query)

                if not dados:
                    messagebox.showinfo("Aviso", "Não há dados suficientes para gerar este relatório.")
                    return

                # Cabeçalho da tabela
                table_data = [
                    ["ID", "Descrição", "Ação Corretiva", "Prazo", "Status", "Data Inspeção", "Posto", "Vigilante"]]

                # Dados da tabela
                for d in dados:
                    table_data.append([
                        d[0], d[2], d[3], d[4], d[5], d[6], d[7], d[8]
                    ])

            elif tipo_relatorio == "Inspeções por Supervisor":
                query = """
                SELECT i.id_inspecao, s.nome as supervisor, v.nome as vigilante, 
                       p.nome as posto, i.data_inspecao, i.observacoes
                FROM inspecoes i
                JOIN supervisores s ON i.id_supervisor = s.id_supervisor
                JOIN vigilantes v ON i.id_vigilante = v.id_vigilante
                JOIN postos p ON i.id_posto = p.id_posto
                ORDER BY s.nome, i.data_inspecao DESC
                """
                dados = self.db.fetch_all(query)

                if not dados:
                    messagebox.showinfo("Aviso", "Não há dados suficientes para gerar este relatório.")
                    return

                # Cabeçalho da tabela
                table_data = [["ID", "Supervisor", "Vigilante", "Posto", "Data Inspeção", "Observações"]]

                # Dados da tabela
                for d in dados:
                    table_data.append([d[0], d[1], d[2], d[3], d[4], d[5]])

            elif tipo_relatorio == "Vigilantes Ativos/Inativos":
                query = """
                SELECT id_vigilante, nome, matricula, cnv, 
                       CASE WHEN ativo = 1 THEN 'Ativo' ELSE 'Inativo' END as status,
                       criado_em
                FROM vigilantes
                ORDER BY ativo DESC, nome
                """
                dados = self.db.fetch_all(query)

                if not dados:
                    messagebox.showinfo("Aviso", "Não há dados suficientes para gerar este relatório.")
                    return

                # Cabeçalho da tabela
                table_data = [["ID", "Nome", "Matrícula", "CNV", "Status", "Criado em"]]

                # Dados da tabela
                for d in dados:
                    table_data.append([d[0], d[1], d[2], d[3], d[4], d[5]])

            elif tipo_relatorio == "Postos Ativos/Inativos":
                query = """
                SELECT id_posto, nome, endereco, 
                       CASE WHEN ativo = 1 THEN 'Ativo' ELSE 'Inativo' END as status,
                       criado_em
                FROM postos
                ORDER BY ativo DESC, nome
                """
                dados = self.db.fetch_all(query)

                if not dados:
                    messagebox.showinfo("Aviso", "Não há dados suficientes para gerar este relatório.")
                    return

                # Cabeçalho da tabela
                table_data = [["ID", "Nome", "Endereço", "Status", "Criado em"]]

                # Dados da tabela
                for d in dados:
                    table_data.append([d[0], d[1], d[2], d[3], d[4]])

            # Criar tabela
            table = Table(table_data)

            # Estilo da tabela
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            elements.append(table)

            # Gerar PDF
            doc.build(elements)

            messagebox.showinfo("Sucesso", f"Relatório '{tipo_relatorio}' exportado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar PDF: {str(e)}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
