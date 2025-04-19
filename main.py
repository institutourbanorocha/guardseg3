from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.utils import platform
from kivy.clock import Clock
import sqlite3
import os
import csv
from datetime import datetime
import io
from PIL import Image

# Configurar caminho do banco de dados
def get_db_path():
    if platform == 'android':
        from android.storage import app_storage_path
        return os.path.join(app_storage_path(), 'SUPERVISOR.DB')
    else:
        return 'SUPERVISOR.DB'

# Classe base para telas de dados
class BaseDataScreen(Screen):
    tabela = ''
    campos = []
    colunas = []
    
    def on_enter(self):
        self.carregar_dados()
    
    def carregar_dados(self):
        try:
            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {self.tabela}")
            dados = cursor.fetchall()
            conn.close()
            
            # Limpar dados anteriores
            if hasattr(self.ids, 'data_table'):
                self.ids.box_layout.remove_widget(self.ids.data_table)
            
            # Criar nova tabela
            self.data_table = MDDataTable(
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                size_hint=(0.9, 0.6),
                use_pagination=True,
                column_data=self.colunas,
                row_data=dados
            )
            self.ids.box_layout.add_widget(self.data_table)
            
            # Configurar eventos
            self.data_table.bind(on_row_press=self.on_row_press)
        except Exception as e:
            self.mostrar_dialogo(f"Erro ao carregar dados: {str(e)}")
    
    def on_row_press(self, instance_table, instance_row):
        row_data = instance_row.text
        self.mostrar_opcoes(row_data)
    
    def mostrar_opcoes(self, row_data):
        dialog = MDDialog(
            title="Opções",
            text=f"Selecione uma ação para o registro {row_data[0]}",
            buttons=[
                MDFlatButton(
                    text="Editar",
                    on_release=lambda x: self.editar_item(row_data)
                ),
                MDFlatButton(
                    text="Excluir",
                    on_release=lambda x: self.excluir_item(row_data)
                ),
                MDFlatButton(
                    text="Cancelar",
                    on_release=lambda x: dialog.dismiss()
                ),
            ],
        )
        dialog.open()
    
    def adicionar_item(self):
        self.manager.get_screen('formulario').configurar(self.tabela, self.campos)
        self.manager.current = 'formulario'
    
    def editar_item(self, row_data):
        self.manager.get_screen('formulario').configurar(self.tabela, self.campos, row_data)
        self.manager.current = 'formulario'
    
    def excluir_item(self, row_data):
        dialog = MDDialog(
            title="Confirmar Exclusão",
            text=f"Tem certeza que deseja excluir este registro?",
            buttons=[
                MDFlatButton(
                    text="Sim",
                    on_release=lambda x: self.confirmar_exclusao(row_data, dialog)
                ),
                MDFlatButton(
                    text="Não",
                    on_release=lambda x: dialog.dismiss()
                ),
            ],
        )
        dialog.open()
    
    def confirmar_exclusao(self, row_data, dialog):
        try:
            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()
            id_campo = f"id_{self.tabela[:-1] if self.tabela.endswith('s') else self.tabela}"
            cursor.execute(f"DELETE FROM {self.tabela} WHERE {id_campo} = ?", (row_data[0],))
            conn.commit()
            conn.close()
            dialog.dismiss()
            self.carregar_dados()
            self.mostrar_dialogo("Registro excluído com sucesso!")
        except Exception as e:
            dialog.dismiss()
            self.mostrar_dialogo(f"Erro ao excluir: {str(e)}")
    
    def importar_csv(self):
        if platform == 'android':
            self.selecionar_arquivo_csv()
        else:
            self.mostrar_dialogo("Importação CSV disponível apenas no Android")
    
    def selecionar_arquivo_csv(self):
        from android.storage import primary_external_storage_path
        from android import activity
        from jnius import autoclass
        
        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')
        
        intent = Intent(Intent.ACTION_GET_CONTENT)
        intent.setType("text/csv")
        activity.startActivityForResult(intent, 1)
        
        # Configurar callback para resultado
        activity.bind(on_activity_result=self.on_activity_result)
    
    def on_activity_result(self, request_code, result_code, intent):
        if request_code == 1 and result_code == -1:  # RESULT_OK
            uri = intent.getData()
            self.processar_csv(uri)
    
    def processar_csv(self, uri):
        try:
            from jnius import autoclass
            
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity.getApplicationContext()
            
            inputStream = context.getContentResolver().openInputStream(uri)
            reader = autoclass('java.io.InputStreamReader')(inputStream)
            bufferedReader = autoclass('java.io.BufferedReader')(reader)
            
            linha = bufferedReader.readLine()  # Cabeçalho
            colunas = linha.split(',')
            
            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()
            
            while True:
                linha = bufferedReader.readLine()
                if not linha:
                    break
                    
                valores = linha.split(',')
                placeholders = ','.join(['?' for _ in valores])
                query = f"INSERT INTO {self.tabela} ({','.join(colunas)}) VALUES ({placeholders})"
                cursor.execute(query, valores)
            
            conn.commit()
            conn.close()
            bufferedReader.close()
            
            self.carregar_dados()
            self.mostrar_dialogo("Importação concluída com sucesso!")
        except Exception as e:
            self.mostrar_dialogo(f"Erro ao importar CSV: {str(e)}")
    
    def mostrar_dialogo(self, mensagem):
        dialog = MDDialog(
            title="Aviso",
            text=mensagem,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                ),
            ],
        )
        dialog.open()

# Tela principal
class MainScreen(Screen):
    pass

# Tela de formulário
class FormularioScreen(Screen):
    def configurar(self, tabela, campos, dados=None):
        self.tabela = tabela
        self.campos = campos
        self.dados = dados
        self.id_valor = dados[0] if dados else None
        
        # Limpar formulário anterior
        self.ids.form_layout.clear_widgets()
        
        # Preencher formulário
        from kivymd.uix.textfield import MDTextField
        from kivymd.uix.button import MDRaisedButton
        
        for i, campo in enumerate(campos):
            if campo['tipo'] == 'texto':
                textfield = MDTextField(
                    hint_text=campo['label'],
                    helper_text=campo.get('helper', ''),
                    helper_text_mode="on_focus",
                    pos_hint={'center_x': 0.5},
                    size_hint_x=0.8,
                )
                if dados and i+1 < len(dados):
                    textfield.text = str(dados[i+1] or '')
                self.ids.form_layout.add_widget(textfield)
                campo['widget'] = textfield
            
            elif campo['tipo'] == 'dropdown':
                textfield = MDTextField(
                    hint_text=campo['label'],
                    helper_text="Toque para selecionar",
                    helper_text_mode="on_focus",
                    pos_hint={'center_x': 0.5},
                    size_hint_x=0.8,
                    disabled=True
                )
                if dados and i+1 < len(dados):
                    textfield.text = str(dados[i+1] or '')
                self.ids.form_layout.add_widget(textfield)
                campo['widget'] = textfield
                
                # Configurar menu dropdown
                menu_items = [
                    {
                        "text": item,
                        "viewclass": "OneLineListItem",
                        "on_release": lambda x=item, tf=textfield: self.selecionar_dropdown(tf, x),
                    } for item in campo.get('opcoes', [])
                ]
                
                dropdown = MDDropdownMenu(
                    caller=textfield,
                    items=menu_items,
                    width_mult=4,
                )
                campo['dropdown'] = dropdown
                
                # Vincular evento de toque
                textfield.bind(on_touch_down=lambda instance, touch, tf=textfield, dd=dropdown: 
                               self.abrir_dropdown(instance, touch, tf, dd))
    
    def abrir_dropdown(self, instance, touch, textfield, dropdown):
        if textfield.collide_point(*touch.pos):
            dropdown.open()
    
    def selecionar_dropdown(self, textfield, valor):
        textfield.text = str(valor)
        for campo in self.campos:
            if 'widget' in campo and campo['widget'] == textfield:
                campo['dropdown'].dismiss()
    
    def salvar(self):
        # Coletar dados do formulário
        valores = {}
        for campo in self.campos:
            if 'widget' in campo:
                valores[campo['nome']] = campo['widget'].text
        
        try:
            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()
            
            if self.id_valor:  # Atualizar
                set_clause = ', '.join([f"{k} = ?" for k in valores.keys()])
                id_campo = f"id_{self.tabela[:-1] if self.tabela.endswith('s') else self.tabela}"
                query = f"UPDATE {self.tabela} SET {set_clause} WHERE {id_campo} = ?"
                params = list(valores.values())
                params.append(self.id_valor)
                cursor.execute(query, params)
            else:  # Inserir
                colunas = ', '.join(valores.keys())
                placeholders = ', '.join(['?' for _ in valores])
                query = f"INSERT INTO {self.tabela} ({colunas}) VALUES ({placeholders})"
                cursor.execute(query, list(valores.values()))
            
            conn.commit()
            conn.close()
            
            # Voltar para a tela anterior
            self.manager.current = self.tabela
            
            # Atualizar dados
            self.manager.get_screen(self.tabela).carregar_dados()
            
        except Exception as e:
            self.mostrar_dialogo(f"Erro ao salvar: {str(e)}")
    
    def mostrar_dialogo(self, mensagem):
        dialog = MDDialog(
            title="Aviso",
            text=mensagem,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                ),
            ],
        )
        dialog.open()

# Telas específicas
class SupervisoresScreen(BaseDataScreen):
    tabela = 'supervisores'
    colunas = [
        ("ID", dp(30)),
        ("Nome", dp(60)),
        ("Matrícula", dp(40)),
        ("Email", dp(60)),
        ("Ativo", dp(30))
    ]
    campos = [
        {'nome': 'nome', 'tipo': 'texto', 'label': 'Nome'},
        {'nome': 'matricula', 'tipo': 'texto', 'label': 'Matrícula'},
        {'nome': 'email', 'tipo': 'texto', 'label': 'Email'},
        {'nome': 'ativo', 'tipo': 'dropdown', 'label': 'Ativo', 'opcoes': ['1', '0']}
    ]

class VigilantesScreen(BaseDataScreen):
    tabela = 'vigilantes'
    colunas = [
        ("ID", dp(30)),
        ("Nome", dp(60)),
        ("Matrícula", dp(40)),
        ("CNV", dp(40)),
        ("Ativo", dp(30))
    ]
    campos = [
        {'nome': 'nome', 'tipo': 'texto', 'label': 'Nome'},
        {'nome': 'matricula', 'tipo': 'texto', 'label': 'Matrícula'},
        {'nome': 'cnv', 'tipo': 'texto', 'label': 'CNV'},
        {'nome': 'ativo', 'tipo': 'dropdown', 'label': 'Ativo', 'opcoes': ['1', '0']}
    ]

class PostosScreen(BaseDataScreen):
    tabela = 'postos'
    colunas = [
        ("ID", dp(30)),
        ("Nome", dp(60)),
        ("Endereço", dp(80)),
        ("Ativo", dp(30))
    ]
    campos = [
        {'nome': 'nome', 'tipo': 'texto', 'label': 'Nome'},
        {'nome': 'endereco', 'tipo': 'texto', 'label': 'Endereço'},
        {'nome': 'ativo', 'tipo': 'dropdown', 'label': 'Ativo', 'opcoes': ['1', '0']}
    ]

class InspecoesScreen(BaseDataScreen):
    tabela = 'inspecoes'
    colunas = [
        ("ID", dp(30)),
        ("Supervisor", dp(40)),
        ("Vigilante", dp(40)),
        ("Posto", dp(40)),
        ("Data", dp(60)),
        ("Observações", dp(80))
    ]
    campos = [
        {'nome': 'id_supervisor', 'tipo': 'dropdown', 'label': 'Supervisor', 'opcoes': []},
        {'nome': 'id_vigilante', 'tipo': 'dropdown', 'label': 'Vigilante', 'opcoes': []},
        {'nome': 'id_posto', 'tipo': 'dropdown', 'label': 'Posto', 'opcoes': []},
        {'nome': 'data_inspecao', 'tipo': 'texto', 'label': 'Data (YYYY-MM-DD HH:MM:SS)'},
        {'nome': 'observacoes', 'tipo': 'texto', 'label': 'Observações'}
    ]
    
    def on_enter(self):
        # Atualizar opções de dropdown
        self.atualizar_opcoes_dropdown()
        super().on_enter()
    
    def atualizar_opcoes_dropdown(self):
        try:
            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()
            
            # Supervisores
            cursor.execute("SELECT id_supervisor, nome FROM supervisores")
            supervisores = cursor.fetchall()
            self.campos[0]['opcoes'] = [str(s[0]) for s in supervisores]
            
            # Vigilantes
            cursor.execute("SELECT id_vigilante, nome FROM vigilantes")
            vigilantes = cursor.fetchall()
            self.campos[1]['opcoes'] = [str(v[0]) for v in vigilantes]
            
            # Postos
            cursor.execute("SELECT id_posto, nome FROM postos")
            postos = cursor.fetchall()
            self.campos[2]['opcoes'] = [str(p[0]) for p in postos]
            
            conn.close()
        except Exception as e:
            self.mostrar_dialogo(f"Erro ao carregar opções: {str(e)}")

class ApontamentosScreen(BaseDataScreen):
    tabela = 'apontamentos'
    colunas = [
        ("ID", dp(30)),
        ("Inspeção", dp(30)),
        ("EPI", dp(30)),
        ("Posto", dp(30)),
        ("Armamento", dp(30)),
        ("Documentação", dp(30)),
        ("Saúde", dp(30)),
        ("Procedimentos", dp(30))
    ]
    campos = [
        {'nome': 'id_inspecao', 'tipo': 'dropdown', 'label': 'Inspeção', 'opcoes': []},
        {'nome': 'epi_conforme', 'tipo': 'dropdown', 'label': 'EPI Conforme', 'opcoes': ['1', '0']},
        {'nome': 'epi_observacao', 'tipo': 'texto', 'label': 'Observação EPI'},
        {'nome': 'posto_conforme', 'tipo': 'dropdown', 'label': 'Posto Conforme', 'opcoes': ['1', '0']},
        {'nome': 'posto_observacao', 'tipo': 'texto', 'label': 'Observação Posto'},
        {'nome': 'armamento_conforme', 'tipo': 'dropdown', 'label': 'Armamento Conforme', 'opcoes': ['1', '0']},
        {'nome': 'armamento_observacao', 'tipo': 'texto', 'label': 'Observação Armamento'},
        {'nome': 'documentacao_conforme', 'tipo': 'dropdown', 'label': 'Documentação Conforme', 'opcoes': ['1', '0']},
        {'nome': 'documentacao_observacao', 'tipo': 'texto', 'label': 'Observação Documentação'},
        {'nome': 'saude_psicofisica_conforme', 'tipo': 'dropdown', 'label': 'Saúde Conforme', 'opcoes': ['1', '0']},
        {'nome': 'saude_observacao', 'tipo': 'texto', 'label': 'Observação Saúde'},
        {'nome': 'procedimentos_conforme', 'tipo': 'dropdown', 'label': 'Procedimentos Conforme', 'opcoes': ['1', '0']},
        {'nome': 'procedimentos_observacao', 'tipo': 'texto', 'label': 'Observação Procedimentos'}
    ]
    
    def on_enter(self):
        # Atualizar opções de dropdown
        self.atualizar_opcoes_dropdown()
        super().on_enter()
    
    def atualizar_opcoes_dropdown(self):
        try:
            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()
            
            # Inspeções
            cursor.execute("SELECT id_inspecao FROM inspecoes")
            inspecoes = cursor.fetchall()
            self.campos[0]['opcoes'] = [str(i[0]) for i in inspecoes]
            
            conn.close()
        except Exception as e:
            self.mostrar_dialogo(f"Erro ao carregar opções: {str(e)}")

class NaoConformidadesScreen(BaseDataScreen):
    tabela = 'nao_conformidades'
    colunas = [
        ("ID", dp(30)),
        ("Apontamento", dp(30)),
        ("Descrição", dp(80)),
        ("Ação Corretiva", dp(80)),
        ("Prazo", dp(40)),
        ("Status", dp(40))
    ]
    campos = [
        {'nome': 'id_apontamento', 'tipo': 'dropdown', 'label': 'Apontamento', 'opcoes': []},
        {'nome': 'descricao', 'tipo': 'texto', 'label': 'Descrição'},
        {'nome': 'acao_corretiva', 'tipo': 'texto', 'label': 'Ação Corretiva'},
        {'nome': 'prazo_acoes', 'tipo': 'texto', 'label': 'Prazo (YYYY-MM-DD)'},
        {'nome': 'status', 'tipo': 'dropdown', 'label': 'Status', 'opcoes': ['Pendente', 'Em Andamento', 'Concluído']}
    ]
    
    def on_enter(self):
        # Atualizar opções de dropdown
        self.atualizar_opcoes_dropdown()
        super().on_enter()
    
    def atualizar_opcoes_dropdown(self):
        try:
            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()
            
            # Apontamentos
            cursor.execute("SELECT id_apontamento FROM apontamentos")
            apontamentos = cursor.fetchall()
            self.campos[0]['opcoes'] = [str(a[0]) for a in apontamentos]
            
            conn.close()
        except Exception as e:
            self.mostrar_dialogo(f"Erro ao carregar opções: {str(e)}")

# Aplicativo principal
class SupervisorApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Light"
        
        # Carregar arquivo KV
        return Builder.load_file('supervisor.kv')
    
    def on_start(self):
        # Inicializar banco de dados
        self.criar_banco_dados()
        
        # Solicitar permissões no Android
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])
    
    def criar_banco_dados(self):
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Criar tabelas
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
        conn.close()

if __name__ == '__main__':
    SupervisorApp().run()