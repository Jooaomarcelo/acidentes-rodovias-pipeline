import pandas as pd
from typing import List
from pipeline.extractors import BaseExtractor
from pipeline.transformers import BaseTransformer
from pipeline.loaders import BaseLoader

class ETLPipeline:
    """
    Orquestrador que gerencia o fluxo de ETL para um conjunto de dados específico.
    """
    def __init__(self, extractor: BaseExtractor, transformer: BaseTransformer, loaders: List[BaseLoader], table_name: str):
        self.extractor = extractor
        self.transformer = transformer
        self.loaders = loaders
        self.table_name = table_name

    def run(self):
        print(f"\n========================================")
        print(f"Iniciando pipeline para a tabela: {self.table_name}")
        print(f"========================================")
        
        try:
            # 1. Extração
            df_raw = self.extractor.extract()
            print(f"Extração concluída. Registros obtidos: {len(df_raw)}")
            
            # 2. Transformação
            df_clean = self.transformer.transform(df_raw)
            print(f"Transformação concluída. Registros resultantes: {len(df_clean)}")
            
            # 3. Carga
            for loader in self.loaders:
                loader.load(df_clean, self.table_name)
                
            print(f"Pipeline '{self.table_name}' executado com sucesso!")
            
        except Exception as e:
            print(f"Falha na execução do pipeline '{self.table_name}': {e}")
            raise e
