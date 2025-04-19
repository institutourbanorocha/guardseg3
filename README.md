# Sistema de Supervisão de Vigilantes

Um sistema completo para gerenciamento de supervisores, vigilantes, postos, inspeções, apontamentos e não conformidades.

## Funcionalidades

- CRUD completo para todas as entidades (Supervisores, Vigilantes, Postos, Inspeções, Apontamentos, Não Conformidades)
- Importação de dados via CSV
- Geração de relatórios em PDF
- Visualização de gráficos estatísticos
- Interface responsiva e amigável

## Estrutura do Banco de Dados

O sistema utiliza SQLite com as seguintes tabelas:

- **vigilantes**: Cadastro de vigilantes
- **supervisores**: Cadastro de supervisores
- **postos**: Cadastro de postos de vigilância
- **inspecoes**: Registro de inspeções realizadas
- **apontamentos**: Registro de conformidades e observações
- **nao_conformidades**: Registro de não conformidades e ações corretivas

## Requisitos

- Python 3.6+
- Bibliotecas: tkinter, sqlite3, pandas, matplotlib, reportlab, pillow

## Instalação

1. Clone o repositório:
\`\`\`
git clone https://github.com/seu-usuario/sistema-supervisao.git
cd sistema-supervisao
\`\`\`

2. Instale as dependências:
\`\`\`
pip install pandas matplotlib reportlab pillow
\`\`\`

3. Execute o aplicativo:
\`\`\`
python app.py
\`\`\`

## Importação de Dados

O sistema permite importar dados via arquivos CSV. Os arquivos devem seguir o formato:

- **supervisores.csv**: nome,matricula,email,ativo
- **vigilantes.csv**: nome,matricula,cnv,ativo
- **postos.csv**: nome,endereco,ativo

Para gerar arquivos CSV de exemplo e inserir dados de teste:

\`\`\`
python import_sample_data.py
\`\`\`

## Relatórios

O sistema gera relatórios em PDF com gráficos e tabelas. Para gerar relatórios de exemplo:

\`\`\`
python generate_reports.py
\`\`\`

Os relatórios são salvos na pasta `reports/`.

## Uso do Sistema

1. Na tela inicial, selecione a entidade que deseja gerenciar
2. Use os botões para adicionar, editar ou excluir registros
3. Para importar dados, clique no botão "Importar CSV"
4. Para gerar relatórios, acesse a aba "Relatórios"

## Licença

Este projeto está licenciado sob a licença MIT.
\`\`\`

## Explicação do Sistema

O sistema de supervisão de vigilantes que desenvolvi é uma aplicação completa em Python com banco de dados SQLite, que permite gerenciar todo o processo de supervisão de vigilantes em postos de segurança. Ele inclui:

1. **Interface Gráfica Responsiva**: Utilizando Tkinter para desktop e com suporte para KivyMD em dispositivos móveis.

2. **CRUD Completo**: Operações de Criar, Ler, Atualizar e Deletar para todas as entidades do sistema:
   - Supervisores
   - Vigilantes
   - Postos
   - Inspeções
   - Apontamentos
   - Não Conformidades

3. **Importação CSV**: Funcionalidade para importar dados em massa via arquivos CSV.

4. **Relatórios**: Geração de relatórios em PDF com gráficos e tabelas para análise de:
   - Conformidade por posto
   - Não conformidades por status
   - Inspeções por supervisor
   - Status de vigilantes e postos

5. **Visualização de Dados**: Gráficos estatísticos para análise visual dos dados.

6. **Banco de Dados Relacional**: Estrutura de banco de dados SQLite com relacionamentos entre as tabelas.

O sistema é ideal para empresas de segurança que precisam gerenciar suas equipes de vigilantes, realizar inspeções periódicas e controlar não conformidades encontradas durante as inspeções.

<Actions>
  <Action name="Executar o sistema" description="Execute o arquivo app.py para iniciar o sistema" />
  <Action name="Importar dados de exemplo" description="Execute import_sample_data.py para criar dados de teste" />
  <Action name="Gerar relatórios" description="Execute generate_reports.py para criar relatórios em PDF" />
  <Action name="Adaptar para Android" description="Adapte o sistema para rodar em dispositivos Android usando KivyMD" />
  <Action name="Adicionar autenticação" description="Implemente um sistema de login para controle de acesso" />
</Actions>

\`\`\`

