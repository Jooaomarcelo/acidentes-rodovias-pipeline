import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env (se existir)
load_dotenv()

# Caminhos padrão do projeto
DADOS_DIR = os.getenv("DADOS_DIR")
if not DADOS_DIR:
    DADOS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "dados"))
else:
    DADOS_DIR = os.path.abspath(DADOS_DIR)

OUTPUT_DIR = os.path.join(DADOS_DIR, "processados")

def get_db_credentials():
    """
    Obtém as configurações de conexão com o PostgreSQL a partir das variáveis
    de ambiente (carregadas do .env) ou solicita de forma interativa.
    """
    host = os.getenv("DB_HOST")
    port_env = os.getenv("DB_PORT")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    
    # Se pelo menos os campos obrigatórios (nome do banco e usuário) estiverem no ambiente,
    # usamos diretamente as credenciais do ambiente/dotenv.
    if database and username:
        port = int(port_env) if port_env and port_env.isdigit() else 5432
        host = host or "localhost"
        return {
            "host": host,
            "port": port,
            "database": database,
            "username": username,
            "password": password or ""
        }
        
    # Caso contrário, solicita interativamente ao usuário as configurações
    print("\n--- Configurações de Conexão com o PostgreSQL ---")
    print("Nota: Você pode configurar estas variáveis em um arquivo .env para evitar este prompt.")
    
    host_input = input("Host do Banco [localhost]: ").strip() or "localhost"
    
    port_input = input("Porta do Banco [5432]: ").strip()
    port = int(port_input) if port_input.isdigit() else 5432
    
    database_input = input("Nome do Banco de Dados: ").strip()
    while not database_input:
        print("Erro: O nome do banco de dados é obrigatório.")
        database_input = input("Nome do Banco de Dados: ").strip()
        
    username_input = input("Usuário: ").strip()
    while not username_input:
        print("Erro: O usuário é obrigatório.")
        username_input = input("Usuário: ").strip()
        
    password_input = input("Senha: ").strip()
    
    return {
        "host": host_input,
        "port": port,
        "database": database_input,
        "username": username_input,
        "password": password_input
    }

