import sqlite3
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import numpy as np

def get_db_path():
    return 'SUPERVISOR.DB'

def create_reports_directory():
    if not os.path.exists('reports'):
        os.makedirs('reports')
    return 'reports'

def generate_conformity_report():
    db_path = get_db_path()
    reports_dir = create_reports_directory()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
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
    cursor.execute(query)
    dados = cursor.fetchall()
    
    if not dados:
        print("Não há dados suficientes para gerar o relatório de conformidade.")
        return
    
    # Criar documento PDF
    pdf_path = os.path.join(reports_dir, f'conformidade_postos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
    doc = SimpleDocTemplate(pdf_path, pagesize=landscape(letter))
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    subtitle_style = styles["Heading2"]
    normal_style = styles["Normal"]
    
    # Título
    elements.append(Paragraph("Relatório de Conformidade por Posto", title_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
    elements.append(Spacer(1, 24))
    
    # Cabeçalho da tabela
    table_data = [["Posto", "EPI", "Posto", "Armamento", "Documentação", "Saúde", "Procedimentos", "% Conformidade"]]
    
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
    elements.append(Spacer(1, 24))
    
    # Criar gráfico
    plt.figure(figsize=(10, 6))
    
    # Preparar dados para o gráfico
    postos = [d[0] for d in dados]
    conformidade = [(d[1] + d[2] + d[3] + d[4] + d[5] + d[6]) / (d[7] * 6) * 100 if d[7] > 0 else 0 for d in dados]
    
    # Criar gráfico de barras
    plt.bar(postos, conformidade, color='skyblue')
    plt.xlabel('Postos')
    plt.ylabel('% Conformidade')
    plt.title('Conformidade por Posto')
    plt.ylim(0, 100)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Salvar gráfico
    chart_path = os.path.join(reports_dir, 'temp_chart.png')
    plt.savefig(chart_path)
    plt.close()
    
    # Adicionar gráfico ao PDF
    elements.append(Paragraph("Gráfico de Conformidade", subtitle_style))
    elements.append(Spacer(1, 12))
    elements.append(Image(chart_path, width=500, height=300))
    
    # Gerar PDF
    doc.build(elements)
    
    # Remover arquivo temporário
    os.remove(chart_path)
    
    print(f"Relatório de conformidade gerado: {pdf_path}")
    
    conn.close()

def generate_nonconformity_report():
    db_path = get_db_path()
    reports_dir = create_reports_directory()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Consulta para obter dados de não conformidades
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
    cursor.execute(query)
    dados = cursor.fetchall()
    
    if not dados:
        print("Não há dados suficientes para gerar o relatório de não conformidades.")
        return
    
    # Criar documento PDF
    pdf_path = os.path.join(reports_dir, f'nao_conformidades_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
    doc = SimpleDocTemplate(pdf_path, pagesize=landscape(letter))
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    subtitle_style = styles["Heading2"]
    normal_style = styles["Normal"]
    
    # Título
    elements.append(Paragraph("Relatório de Não Conformidades", title_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
    elements.append(Spacer(1, 24))
    
    # Cabeçalho da tabela
    table_data = [["ID", "Descrição", "Ação Corretiva", "Prazo", "Status", "Data Inspeção", "Posto", "Vigilante"]]
    
    # Dados da tabela
    for d in dados:
        table_data.append([
            d[0], d[2], d[3], d[4], d[5], d[6], d[7], d[8]
        ])
    
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
    elements.append(Spacer(1, 24))
    
    # Consulta para obter dados de não conformidades por status
    query = """
    SELECT status, COUNT(*) as total
    FROM nao_conformidades
    GROUP BY status
    """
    cursor.execute(query)
    dados_status = cursor.fetchall()
    
    if dados_status:
        # Criar gráfico
        plt.figure(figsize=(8, 8))
        
        # Preparar dados para o gráfico
        status = [d[0] for d in dados_status]
        totais = [d[1] for d in dados_status]
        
        # Criar gráfico de pizza
        plt.pie(totais, labels=status, autopct='%1.1f%%', startangle=90, colors=['red', 'orange', 'green'])
        plt.title('Não Conformidades por Status')
        plt.axis('equal')
        plt.tight_layout()
        
        # Salvar gráfico
        chart_path = os.path.join(reports_dir, 'temp_chart.png')
        plt.savefig(chart_path)
        plt.close()
        
        # Adicionar gráfico ao PDF
        elements.append(Paragraph("Distribuição por Status", subtitle_style))
        elements.append(Spacer(1, 12))
        elements.append(Image(chart_path, width=400, height=400))
        
        # Remover arquivo temporário
        os.remove(chart_path)
    
    # Gerar PDF
    doc.build(elements)
    
    print(f"Relatório de não conformidades gerado: {pdf_path}")
    
    conn.close()

def generate_inspection_report():
    db_path = get_db_path()
    reports_dir = create_reports_directory()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Consulta para obter dados de inspeções
    query = """
    SELECT i.id_inspecao, s.nome as supervisor, v.nome as vigilante, 
           p.nome as posto, i.data_inspecao, i.observacoes
    FROM inspecoes i
    JOIN supervisores s ON i.id_supervisor = s.id_supervisor
    JOIN vigilantes v ON i.id_vigilante = v.id_vigilante
    JOIN postos p ON i.id_posto = p.id_posto
    ORDER BY i.data_inspecao DESC
    """
    cursor.execute(query)
    dados = cursor.fetchall()
    
    if not dados:
        print("Não há dados suficientes para gerar o relatório de inspeções.")
        return
    
    # Criar documento PDF
    pdf_path = os.path.join(reports_dir, f'inspecoes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
    doc = SimpleDocTemplate(pdf_path, pagesize=landscape(letter))
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    subtitle_style = styles["Heading2"]
    normal_style = styles["Normal"]
    
    # Título
    elements.append(Paragraph("Relatório de Inspeções", title_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
    elements.append(Spacer(1, 24))
    
    # Cabeçalho da tabela
    table_data = [["ID", "Supervisor", "Vigilante", "Posto", "Data Inspeção", "Observações"]]
    
    # Dados da tabela
    for d in dados:
        table_data.append([d[0], d[1], d[2], d[3], d[4], d[5]])
    
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
    elements.append(Spacer(1, 24))
    
    # Consulta para obter dados de inspeções por supervisor
    query = """
    SELECT s.nome, COUNT(i.id_inspecao) as total
    FROM inspecoes i
    JOIN supervisores s ON i.id_supervisor = s.id_supervisor
    GROUP BY s.nome
    """
    cursor.execute(query)
    dados_supervisor = cursor.fetchall()
    
    if dados_supervisor:
        # Criar gráfico
        plt.figure(figsize=(10, 6))
        
        # Preparar dados para o gráfico
        supervisores = [d[0] for d in dados_supervisor]
        totais = [d[1] for d in dados_supervisor]
        
        # Criar gráfico de barras
        plt.bar(supervisores, totais, color='lightgreen')
        plt.xlabel('Supervisores')
        plt.ylabel('Número de Inspeções')
        plt.title('Inspeções por Supervisor')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Salvar gráfico
        chart_path = os.path.join(reports_dir, 'temp_chart.png')
        plt.savefig(chart_path)
        plt.close()
        
        # Adicionar gráfico ao PDF
        elements.append(Paragraph("Inspeções por Supervisor", subtitle_style))
        elements.append(Spacer(1, 12))
        elements.append(Image(chart_path, width=500, height=300))
        
        # Remover arquivo temporário
        os.remove(chart_path)
    
    # Gerar PDF
    doc.build(elements)
    
    print(f"Relatório de inspeções gerado: {pdf_path}")
    
    conn.close()

if __name__ == "__main__":
    generate_conformity_report()
    generate_nonconformity_report()
    generate_inspection_report()
    print("Todos os relatórios foram gerados com sucesso!")