import os
import sys
from pipeline.config import DADOS_DIR, OUTPUT_DIR, get_db_credentials
from pipeline.extractors import CSVExtractor, ExcelExtractor, JSONExtractor
from pipeline.transformers import AccidentsTransformer, RadarsTransformer, SignalingTransformer
from pipeline.loaders import CSVLoader, PostgreSQLLoader
from pipeline.orchestrator import ETLPipeline

def main():
    print("==================================================")
    print("  Pipeline de ETL - Acidentes e Fiscalização PRF ")
    print("==================================================")
    
    # 1. Definir os Carregadores
    loaders = []
    
    # Sempre adicionamos o CSVLoader para salvar localmente em dados/processados
    csv_loader = CSVLoader(OUTPUT_DIR)
    loaders.append(csv_loader)
    
    # Perguntar ao usuário se deseja conectar ao PostgreSQL
    resposta = input("\nDeseja carregar os dados tratados em um banco PostgreSQL? (S/N): ").strip().upper()
    
    if resposta == 'S':
        try:
            db_config = get_db_credentials()
            # Testar a conexão criando o loader
            postgres_loader = PostgreSQLLoader(db_config)
            loaders.append(postgres_loader)
            print("Carregador PostgreSQL inicializado com sucesso.")
        except Exception as e:
            print(f"\nErro ao configurar a conexão com o PostgreSQL: {e}")
            print("O pipeline prosseguirá gerando APENAS os arquivos CSV locais.")
            # Se deu erro e o usuário digitou S, mantemos apenas o CSVLoader
            loaders = [csv_loader]
            
            # Perguntar se o usuário quer continuar
            continuar = input("\nDeseja continuar apenas com a exportação de CSV locais? (S/N): ").strip().upper()
            if continuar != 'S':
                print("Execução interrompida pelo usuário.")
                sys.exit(0)
    else:
        print("Os dados serão salvos apenas na pasta local como CSV.")

    # 2. Configurar os Pipelines
    
    # A. Pipeline de Acidentes
    acidentes_path = os.path.join(DADOS_DIR, "acidentes", "datatran2026.csv")
    pipe_acidentes = ETLPipeline(
        extractor=CSVExtractor(acidentes_path, sep=';', encoding='latin1'),
        transformer=AccidentsTransformer(),
        loaders=loaders,
        table_name="acidentes"
    )
    
    # B. Pipeline de Radares (PNCV)
    radares_path = os.path.join(DADOS_DIR, "fiscalizacao", "pncv_dados_abertos_12_07_2024.xlsx")
    pipe_radares = ETLPipeline(
        extractor=ExcelExtractor(radares_path, engine_kwargs={'data_only': False}),
        transformer=RadarsTransformer(),
        loaders=loaders,
        table_name="radares_velocidade"
    )
    
    # C. Pipeline de Sinalização
    placas_path = os.path.join(DADOS_DIR, "fiscalizacao", "proibido-ultrapassar-16-06-2026.json")
    pipe_sinalizacao = ETLPipeline(
        extractor=JSONExtractor(placas_path, list_key="proibidoUltrapassar"),
        transformer=SignalingTransformer(),
        loaders=loaders,
        table_name="placas_sinalizacao"
    )
    
    # 3. Executar os Pipelines
    try:
        pipe_acidentes.run()
        pipe_radares.run()
        pipe_sinalizacao.run()
        
        print("\n==================================================")
        print("  Todos os pipelines executados com sucesso!   ")
        print("==================================================")
    except Exception as e:
        print(f"\nOcorreu uma falha durante a execução do pipeline global: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
