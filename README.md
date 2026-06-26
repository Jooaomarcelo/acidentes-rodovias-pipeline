# Pipeline de ETL - Acidentes e Fiscalização nas Rodovias Federais (PRF)

Este projeto implementa um pipeline de ETL (Extração, Transformação e Carga) para processar, integrar e padronizar dados sobre acidentes de trânsito e fiscalização/sinalização em rodovias federais brasileiras. Os dados brutos originados de múltiplas fontes são tratados e consolidados em arquivos CSV locais prontos para análise e, opcionalmente, em um banco de dados relacional PostgreSQL.

---

## 📌 Descrição do Projeto

O pipeline lê e trata dados de três fontes principais de dados abertos relacionados às rodovias federais brasileiras:

1. **Acidentes de Trânsito**: Originados do portal de dados abertos da PRF (ex: `datatran2026.csv`). O pipeline padroniza a representação decimal de quilometragem e coordenadas, além de padronizar a identificação das rodovias federais (ex: de `BR-153` ou `153.0` para `'153'`).
2. **Radares de Velocidade**: Dados do PNCV (Programa Nacional de Controle de Velocidade) em formato Excel (`pncv_dados_abertos_*.xlsx`). Trata a extração de coordenadas geográficas representadas originalmente como fórmulas e limpa colunas vazias ou inconsistentes.
3. **Sinalização Rodoviária**: Trechos de rodovias com proibição de ultrapassagem fornecidos em formato JSON (`proibido-ultrapassar-*.json`). Padroniza as informações de latitude, longitude e quilometragem de início e fim dos trechos.

---

## 📁 Estrutura do Repositório

O repositório está organizado da seguinte forma:

```text
acidentes-rodovias-pipeline/
├── pipeline/
│   ├── __init__.py
│   ├── config.py           # Configurações de caminhos de arquivos e credenciais do banco
│   ├── extractors.py       # Classes extensíveis para extração de CSV, Excel e JSON
│   ├── transformers.py     # Lógica detalhada de limpeza e padronização dos dados
│   ├── loaders.py          # Carregadores de dados para CSV local e PostgreSQL
│   └── orchestrator.py     # Orquestrador geral (ETLPipeline) para acoplamento do fluxo
├── notebooks/
│   └── processamento_dados.ipynb # Análises exploratórias e prototipação das transformações
├── tests/
│   └── test_pipeline.py    # Teste automatizado de integridade e validação dos dados
├── main.py                 # Script de execução interativa principal
├── pyproject.toml          # Configurações de projeto e dependências (PEP 518)
├── uv.lock                 # Lockfile gerado pelo gerenciador 'uv'
└── README.md               # Documentação do projeto (este arquivo)
```

---

## 🛠️ Tecnologias Utilizadas

- **Python** (versão `>= 3.13`)
- **Pandas**: Para manipulação estruturada e transformação eficiente dos dados.
- **SQLAlchemy & Psycopg2**: Para conexão rápida e inserção transacional no PostgreSQL.
- **OpenPyXL**: Engine de leitura do Pandas para lidar com planilhas Excel (.xlsx).
- **UV**: Gerenciador moderno e extremamente rápido de ambientes virtuais e dependências.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos

Por padrão (configurado no [config.py](pipeline/config.py)), o pipeline espera que a pasta contendo os dados brutos esteja em um diretório chamado `dados` na raiz compartilhada (ao lado da pasta deste repositório):

```text
Projeto/
├── acidentes-rodovias-pipeline/    # Repositório do código
└── dados/                          # Pasta com dados de entrada
    ├── acidentes/
    │   └── datatran2026.csv
    ├── fiscalizacao/
    │   ├── pncv_dados_abertos_12_07_2024.xlsx
    │   └── proibido-ultrapassar-16-06-2026.json
    └── processados/                # Pasta de saída (gerada automaticamente se não existir)
```

#### Configurando Variáveis de Ambiente (`.env`)

Você pode configurar caminhos personalizados e dados confidenciais de banco de dados criando um arquivo `.env` na raiz do projeto.

1. Copie o arquivo de exemplo:
   ```bash
   cp .env.example .env
   ```
2. Abra o arquivo `.env` gerado e preencha as variáveis de ambiente necessárias (como as credenciais do PostgreSQL e o caminho da pasta de dados `DADOS_DIR`). Se as credenciais estiverem preenchidas no `.env`, o pipeline as lerá automaticamente sem solicitar interação via console.

---

### Opção 1: Rodando com `uv` (Recomendado)

O projeto está totalmente configurado para uso com o [uv](https://github.com/astral-sh/uv).

1. **Instalar as dependências e criar o ambiente virtual**:
   ```bash
   uv sync
   ```

2. **Executar o pipeline principal**:
   ```bash
   uv run python main.py
   ```
   *Durante a inicialização, o terminal solicitará se você quer exportar os dados para uma base PostgreSQL. Caso responda que não (`N`), o pipeline salvará os resultados apenas localmente no diretório `dados/processados`.*

3. **Executar a suíte de testes de validação**:
   ```bash
   uv run python -m tests.test_pipeline
   ```

---

### Opção 2: Rodando com Pip e Ambiente Virtual Padrão

Caso não utilize o `uv`, siga o fluxo tradicional da linguagem Python:

1. **Criar e ativar o ambiente virtual (venv)**:
   * **Windows (PowerShell)**:
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   * **Windows (CMD)**:
     ```cmd
     python -m venv .venv
     .venv\Scripts\activate.bat
     ```
   * **Linux/macOS**:
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```

2. **Instalar as dependências listadas no projeto**:
   ```bash
   pip install ipykernel openpyxl pandas psycopg2-binary sqlalchemy
   ```

3. **Executar o pipeline**:
   ```bash
   python main.py
   ```

4. **Executar os testes**:
   ```bash
   python -m tests.test_pipeline
   ```

---

## 🛢️ Carga no Banco de Dados (PostgreSQL)

Caso a integração com o banco seja habilitada interativamente ao rodar `main.py`, as seguintes tabelas serão criadas (com substituição completa se já existirem, via política `replace`):

- **`acidentes`**: Dados de acidentes limpos, contendo colunas como rodovia (`br`) padronizada e coordenadas geográficas tratadas.
- **`radares_velocidade`**: Cadastro geral do PNCV de radares de fiscalização eletrônica ativos e inativos com suas respectivas localizações estruturadas.
- **`placas_sinalizacao`**: Extensões de rodovias monitoradas contendo sinalização de proibição de ultrapassagem.

---

## 🔍 Testes e Validação de Qualidade

A execução do arquivo `tests/test_pipeline.py` atua como um portão de qualidade analítica, realizando asserções estruturais importantes sobre o resultado de cada etapa:

- Validação da criação dos arquivos CSV processados em `dados/processados/`.
- Garantia de conversão numérica para ponto flutuante em colunas cruciais de posicionamento geográfico (`latitude`, `longitude`, `km`).
- Garantia de que a expressão de coordenadas em radares (originalmente fórmulas de string no formato `=latitude/longitude`) foi 100% decodificada e recuperada, sem geração de valores nulos inconsistentes.
- Verificação de consistência volumétrica dos datasets.
