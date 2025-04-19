import sqlite3
import os
import csv
from datetime import datetime, timedelta
import random

def get_db_path():
    return 'SUPERVISOR.DB'

def create_sample_csv_files():
    # Criar diretório para arquivos CSV se não existir
    if not os.path.exists('csv_samples'):
        os.makedirs('csv_samples')
    
    # Criar CSV de supervisores
    with open('csv_samples/supervisores.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['nome', 'matricula', 'email', 'ativo'])
        writer.writerow(['João Silva', 'SUP001', 'joao.silva@empresa.com', '1'])
        writer.writerow(['Maria Oliveira', 'SUP002', 'maria.oliveira@empresa.com', '1'])
        writer.writerow(['Carlos Santos', 'SUP003', 'carlos.santos@empresa.com', '1'])
    
    # Criar CSV de vigilantes
    with open('csv_samples/vigilantes.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['nome', 'matricula', 'cnv', 'ativo'])
        writer.writerow(['Pedro Alves', 'VIG001', 'CNV12345', '1'])
        writer.writerow(['Ana Costa', 'VIG002', 'CNV23456', '1'])
        writer.writerow(['Roberto Ferreira', 'VIG003', 'CNV34567', '1'])
        writer.writerow(['Juliana Lima', 'VIG004', 'CNV45678', '1'])
        writer.writerow(['Marcos Souza', 'VIG005', 'CNV56789', '0'])
    
    # Criar CSV de postos
    with open('csv_samples/postos.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['nome', 'endereco', 'ativo'])
        writer.writerow(['Sede Principal', 'Av. Principal, 1000', '1'])
        writer.writerow(['Filial Centro', 'Rua do Centro, 500', '1'])
        writer.writerow(['Depósito Norte', 'Estrada Norte, km 5', '1'])
        writer.writerow(['Loja Shopping', 'Shopping Central, Loja 45', '0'])
    
    print("Arquivos CSV de exemplo criados na pasta 'csv_samples'")

def insert_sample_data():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Inserir supervisores
    supervisores = [
        ('João Silva', 'SUP001', 'joao.silva@empresa.com', 1),
        ('Maria Oliveira', 'SUP002', 'maria.oliveira@empresa.com', 1),
        ('Carlos Santos', 'SUP003', 'carlos.santos@empresa.com', 1)
    ]
    
    for supervisor in supervisores:
        try:
            cursor.execute('''
            INSERT INTO supervisores (nome, matricula, email, ativo)
            VALUES (?, ?, ?, ?)
            ''', supervisor)
        except sqlite3.IntegrityError:
            print(f"Supervisor {supervisor[1]} já existe.")
    
    # Inserir vigilantes
    vigilantes = [
        ('Pedro Alves', 'VIG001', 'CNV12345', 1),
        ('Ana Costa', 'VIG002', 'CNV23456', 1),
        ('Roberto Ferreira', 'VIG003', 'CNV34567', 1),
        ('Juliana Lima', 'VIG004', 'CNV45678', 1),
        ('Marcos Souza', 'VIG005', 'CNV56789', 0)
    ]
    
    for vigilante in vigilantes:
        try:
            cursor.execute('''
            INSERT INTO vigilantes (nome, matricula, cnv, ativo)
            VALUES (?, ?, ?, ?)
            ''', vigilante)
        except sqlite3.IntegrityError:
            print(f"Vigilante {vigilante[1]} já existe.")
    
    # Inserir postos
    postos = [
        ('Sede Principal', 'Av. Principal, 1000', 1),
        ('Filial Centro', 'Rua do Centro, 500', 1),
        ('Depósito Norte', 'Estrada Norte, km 5', 1),
        ('Loja Shopping', 'Shopping Central, Loja 45', 0)
    ]
    
    for posto in postos:
        try:
            cursor.execute('''
            INSERT INTO postos (nome, endereco, ativo)
            VALUES (?, ?, ?)
            ''', posto)
        except sqlite3.IntegrityError:
            print(f"Posto {posto[0]} já existe.")
    
    # Inserir inspeções
    now = datetime.now()
    inspecoes = []
    
    for i in range(10):
        data_inspecao = (now - timedelta(days=i*3)).strftime('%Y-%m-%d %H:%M:%S')
        id_supervisor = random.randint(1, 3)
        id_vigilante = random.randint(1, 4)  # Apenas vigilantes ativos
        id_posto = random.randint(1, 3)  # Apenas postos ativos
        observacoes = f"Inspeção de rotina {i+1}"
        
        inspecoes.append((id_supervisor, id_vigilante, id_posto, data_inspecao, observacoes))
    
    for inspecao in inspecoes:
        cursor.execute('''
        INSERT INTO inspecoes (id_supervisor, id_vigilante, id_posto, data_inspecao, observacoes)
        VALUES (?, ?, ?, ?, ?)
        ''', inspecao)
    
    # Obter IDs das inspeções inseridas
    cursor.execute('SELECT id_inspecao FROM inspecoes')
    ids_inspecoes = [row[0] for row in cursor.fetchall()]
    
    # Inserir apontamentos
    for id_inspecao in ids_inspecoes:
        epi_conforme = random.choice([0, 1])
        epi_obs = "Sem observações" if epi_conforme else "Falta colete"
        
        posto_conforme = random.choice([0, 1])
        posto_obs = "Sem observações" if posto_conforme else "Iluminação inadequada"
        
        armamento_conforme = random.choice([0, 1])
        armamento_obs = "Sem observações" if armamento_conforme else "Falta manutenção"
        
        doc_conforme = random.choice([0, 1])
        doc_obs = "Sem observações" if doc_conforme else "Documentação incompleta"
        
        saude_conforme = random.choice([0, 1])
        saude_obs = "Sem observações" if saude_conforme else "Exame periódico vencido"
        
        proc_conforme = random.choice([0, 1])
        proc_obs = "Sem observações" if proc_conforme else "Não segue procedimento padrão"
        
        cursor.execute('''
        INSERT INTO apontamentos (
            id_inspecao, epi_conforme, epi_observacao, posto_conforme, posto_observacao,
            armamento_conforme, armamento_observacao, documentacao_conforme, documentacao_observacao,
            saude_psicofisica_conforme, saude_observacao, procedimentos_conforme, procedimentos_observacao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            id_inspecao, epi_conforme, epi_obs, posto_conforme, posto_obs,
            armamento_conforme, armamento_obs, doc_conforme, doc_obs,
            saude_conforme, saude_obs, proc_conforme, proc_obs
        ))
    
    # Obter IDs dos apontamentos com não conformidades
    cursor.execute('''
    SELECT a.id_apontamento 
    FROM apontamentos a 
    WHERE a.epi_conforme = 0 OR a.posto_conforme = 0 OR a.armamento_conforme = 0 
       OR a.documentacao_conforme = 0 OR a.saude_psicofisica_conforme = 0 OR a.procedimentos_conforme = 0
    ''')
    ids_apontamentos = [row[0] for row in cursor.fetchall()]
    
    # Inserir não conformidades
    status_options = ['Pendente', 'Em Andamento', 'Concluído']
    
    for id_apontamento in ids_apontamentos:
        # Verificar quais não conformidades existem neste apontamento
        cursor.execute('''
        SELECT epi_conforme, posto_conforme, armamento_conforme, documentacao_conforme,
               saude_psicofisica_conforme, procedimentos_conforme
        FROM apontamentos WHERE id_apontamento = ?
        ''', (id_apontamento,))
        
        conformidades = cursor.fetchone()
        
        if not conformidades[0]:  # EPI não conforme
            descricao = "Falta de EPI adequado"
            acao = "Fornecer EPI completo ao vigilante"
            prazo = (now + timedelta(days=random.randint(5, 15))).strftime('%Y-%m-%d')
            status = random.choice(status_options)
            
            cursor.execute('''
            INSERT INTO nao_conformidades (id_apontamento, descricao, acao_corretiva, prazo_acoes, status)
            VALUES (?, ?, ?, ?, ?)
            ''', (id_apontamento, descricao, acao, prazo, status))
        
        if not conformidades[1]:  # Posto não conforme
            descricao = "Problemas na estrutura do posto"
            acao = "Realizar manutenção no posto"
            prazo = (now + timedelta(days=random.randint(10, 30))).strftime('%Y-%m-%d')
            status = random.choice(status_options)
            
            cursor.execute('''
            INSERT INTO nao_conformidades (id_apontamento, descricao, acao_corretiva, prazo_acoes, status)
            VALUES (?, ?, ?, ?, ?)
            ''', (id_apontamento, descricao, acao, prazo, status))
        
        if not conformidades[2]:  # Armamento não conforme
            descricao = "Armamento com problemas"
            acao = "Enviar para manutenção"
            prazo = (now + timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d')
            status = random.choice(status_options)
            
            cursor.execute('''
            INSERT INTO nao_conformidades (id_apontamento, descricao, acao_corretiva, prazo_acoes, status)
            VALUES (?, ?, ?, ?, ?)
            ''', (id_apontamento, descricao, acao, prazo, status))
    
    conn.commit()
    conn.close()
    
    print("Dados de exemplo inseridos com sucesso!")

if __name__ == "__main__":
    create_sample_csv_files()
    insert_sample_data()