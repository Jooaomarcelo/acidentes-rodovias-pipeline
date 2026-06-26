import os
import sys
import pandas as pd
from pipeline.config import DADOS_DIR, OUTPUT_DIR
from pipeline.extractors import CSVExtractor, ExcelExtractor, JSONExtractor
from pipeline.transformers import AccidentsTransformer, RadarsTransformer, SignalingTransformer
from pipeline.loaders import CSVLoader
from pipeline.orchestrator import ETLPipeline

def verify_pipeline():
    print("==================================================")
    print("  Iniciando Verificação de Teste do Pipeline ETL  ")
    print("==================================================")
    
    # Usaremos apenas o CSVLoader para testes sem necessidade de banco de dados
    test_loaders = [CSVLoader(OUTPUT_DIR)]
    
    # 1. Configurar os Pipelines
    acidentes_path = os.path.join(DADOS_DIR, "acidentes", "datatran2026.csv")
    pipe_acidentes = ETLPipeline(
        extractor=CSVExtractor(acidentes_path, sep=';', encoding='latin1'),
        transformer=AccidentsTransformer(),
        loaders=test_loaders,
        table_name="acidentes"
    )
    
    radares_path = os.path.join(DADOS_DIR, "fiscalizacao", "pncv_dados_abertos_12_07_2024.xlsx")
    pipe_radares = ETLPipeline(
        extractor=ExcelExtractor(radares_path, engine_kwargs={'data_only': False}),
        transformer=RadarsTransformer(),
        loaders=test_loaders,
        table_name="radares_velocidade"
    )
    
    placas_path = os.path.join(DADOS_DIR, "fiscalizacao", "proibido-ultrapassar-16-06-2026.json")
    pipe_sinalizacao = ETLPipeline(
        extractor=JSONExtractor(placas_path, list_key="proibidoUltrapassar"),
        transformer=SignalingTransformer(),
        loaders=test_loaders,
        table_name="placas_sinalizacao"
    )
    
    # 2. Executar os Pipelines
    pipe_acidentes.run()
    pipe_radares.run()
    pipe_sinalizacao.run()
    
    print("\n--- Verificando Integridade dos Arquivos Gerados ---")
    
    # A. Verificando Acidentes
    acid_file = os.path.join(OUTPUT_DIR, "acidentes_processado.csv")
    assert os.path.exists(acid_file), "Erro: acidentes_processado.csv não foi criado."
    df_acid = pd.read_csv(acid_file, sep=';')
    assert pd.api.types.is_float_dtype(df_acid['latitude']), "Erro: latitude dos acidentes não é float."
    assert pd.api.types.is_float_dtype(df_acid['longitude']), "Erro: longitude dos acidentes não é float."
    assert pd.api.types.is_float_dtype(df_acid['km']), "Erro: km dos acidentes não é float."
    print("[OK] acidentes_processado.csv validado com sucesso!")
    
    # B. Verificando Radares
    rad_file = os.path.join(OUTPUT_DIR, "radares_velocidade_processado.csv")
    assert os.path.exists(rad_file), "Erro: radares_velocidade_processado.csv não foi criado."
    df_rad = pd.read_csv(rad_file, sep=';')
    assert len(df_rad) == 1980, f"Erro: radares_velocidade deveria conter 1980 registros, mas tem {len(df_rad)}."
    assert df_rad['latitude'].notnull().sum() == 1980, f"Erro: {1980 - df_rad['latitude'].notnull().sum()} radares ainda possuem coordenadas nulas."
    assert pd.api.types.is_float_dtype(df_rad['latitude']), "Erro: latitude dos radares não é float."
    assert pd.api.types.is_float_dtype(df_rad['longitude']), "Erro: longitude dos radares não é float."
    print("[OK] radares_velocidade_processado.csv validado com sucesso (100% de coordenadas recuperadas)!")
    
    # C. Verificando Placas
    plac_file = os.path.join(OUTPUT_DIR, "placas_sinalizacao_processado.csv")
    assert os.path.exists(plac_file), "Erro: placas_sinalizacao_processado.csv não foi criado."
    df_plac = pd.read_csv(plac_file, sep=';')
    assert pd.api.types.is_float_dtype(df_plac['latitude_inicio']), "Erro: latitude_inicio das placas não é float."
    assert pd.api.types.is_float_dtype(df_plac['latitude_final']), "Erro: latitude_final das placas não é float."
    print("[OK] placas_sinalizacao_processado.csv validado com sucesso!")
    
    print("\n==================================================")
    print("  Todas as validações do teste passaram com sucesso! ")
    print("==================================================")

if __name__ == "__main__":
    try:
        verify_pipeline()
    except AssertionError as e:
        print(f"\n❌ Validação falhou: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro imprevisto: {e}", file=sys.stderr)
        sys.exit(1)
