import os
import pandas as pd
from abc import ABC, abstractmethod
from sqlalchemy import create_engine

class BaseLoader(ABC):
    """
    Classe base abstrata para carregadores de dados.
    """
    @abstractmethod
    def load(self, df: pd.DataFrame, table_name: str):
        """
        Salva o DataFrame no destino especificado.
        """
        pass

class CSVLoader(BaseLoader):
    """
    Carregador que exporta o DataFrame para um arquivo CSV local.
    """
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def load(self, df: pd.DataFrame, table_name: str):
        output_path = os.path.join(self.output_dir, f"{table_name}_processado.csv")
        print(f"Salvando CSV limpo em: {output_path}")
        df.to_csv(output_path, sep=';', index=False, encoding='utf-8')

class PostgreSQLLoader(BaseLoader):
    """
    Carregador que insere o DataFrame em uma tabela do PostgreSQL.
    """
    def __init__(self, db_config: dict):
        self.username = db_config["username"]
        self.password = db_config["password"]
        self.host = db_config["host"]
        self.port = db_config["port"]
        self.database = db_config["database"]
        
        # Monta a string de conexão sqlalchemy para postgresql
        self.conn_string = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        self.engine = create_engine(self.conn_string)

    def load(self, df: pd.DataFrame, table_name: str):
        print(f"Enviando dados para a tabela '{table_name}' no PostgreSQL ({self.host}:{self.port}/{self.database})...")
        try:
            # Salva no banco de dados. Usa 'replace' para recriar a tabela a cada carga
            df.to_sql(table_name, con=self.engine, if_exists='replace', index=False)
            print(f"Tabela '{table_name}' carregada com sucesso!")
        except Exception as e:
            print(f"Erro ao carregar a tabela '{table_name}' no PostgreSQL: {e}")
            raise e
