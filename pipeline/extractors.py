import pandas as pd
import json
from abc import ABC, abstractmethod

class BaseExtractor(ABC):
    """
    Classe base abstrata para extração de dados.
    """
    @abstractmethod
    def extract(self) -> pd.DataFrame:
        """
        Executa a extração dos dados e retorna um pandas DataFrame.
        """
        pass

class CSVExtractor(BaseExtractor):
    """
    Extrator de arquivos CSV.
    """
    def __init__(self, filepath: str, sep: str = ';', encoding: str = 'utf-8', **kwargs):
        self.filepath = filepath
        self.sep = sep
        self.encoding = encoding
        self.kwargs = kwargs

    def extract(self) -> pd.DataFrame:
        print(f"Extraindo CSV: {self.filepath}")
        return pd.read_csv(self.filepath, sep=self.sep, encoding=self.encoding, **self.kwargs)

class ExcelExtractor(BaseExtractor):
    """
    Extrator de arquivos Excel (.xlsx).
    """
    def __init__(self, filepath: str, engine_kwargs: dict = None, **kwargs):
        self.filepath = filepath
        self.engine_kwargs = engine_kwargs or {}
        self.kwargs = kwargs

    def extract(self) -> pd.DataFrame:
        print(f"Extraindo Excel: {self.filepath}")
        return pd.read_excel(self.filepath, engine_kwargs=self.engine_kwargs, **self.kwargs)

class JSONExtractor(BaseExtractor):
    """
    Extrator de arquivos JSON.
    """
    def __init__(self, filepath: str, list_key: str = None, encoding: str = 'utf-8'):
        self.filepath = filepath
        self.list_key = list_key
        self.encoding = encoding

    def extract(self) -> pd.DataFrame:
        print(f"Extraindo JSON: {self.filepath}")
        with open(self.filepath, 'r', encoding=self.encoding) as f:
            data = json.load(f)
            
        if self.list_key:
            if self.list_key in data:
                return pd.DataFrame(data[self.list_key])
            else:
                raise KeyError(f"Chave '{self.list_key}' não encontrada no arquivo JSON.")
        return pd.DataFrame(data)
