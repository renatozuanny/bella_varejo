import pandas as pd
import requests
from datetime import datetime, timedelta, timezone
from google.oauth2 import service_account
import pandas_gbq  # Importado para evitar o FutureWarning no BigQuery


# Parâmetros de Origem e Consumo de API
URL_API = "http://host.docker.internal:8000/api/produtos"
CAMINHO_EXCEL = "/usr/local/airflow/include/catalogo_bella_varejo.xlsx"

# Parâmetros de Destino - Cloud Data Warehouse (Google BigQuery)
PROJECT_ID = "bella-varejo-analytics"
DATASET_ID = "bronze_camada"      # Schema/Dataset destino no BigQuery
TABLE_ID = "fato_pricing_mercado" # Tabela fato bruta de destino
CAMINHO_CHAVE = "/usr/local/airflow/credenciais_gcp.json"

def executar_pipeline_diario(data_carga: str):
    print(f"\n[INFO] Iniciando execução do pipeline - Data Alvo: {data_carga}")
    
    # 1. Extração de dados da API da concorrência
    try:
        resposta = requests.get(URL_API, params={"data": data_carga})
        resposta.raise_for_status()
        dados_api = resposta.json()
        df_mercado = pd.DataFrame(dados_api["produtos"])
        df_mercado = df_mercado.rename(columns={
            "id_produto": "id_produto_interno",
            "preco_concorrente_mercado": "preco_mercado_global"
        })
        print(f"[SUCCESS] {len(df_mercado)} registros extraídos da API do Marketplace.")
    except Exception as e:
        print(f"[ERROR] Falha na extração de dados da API: {e}")
        return

    # 2. Extração de dados do Catálogo Interno de Vendas
    try:
        df_bella = pd.read_excel(CAMINHO_EXCEL)
        df_bella = df_bella[["id_produto_interno", "preco_bella_varejo"]]
        print(f"[SUCCESS] Base de referência interna carregada com sucesso.")
    except Exception as e:
        print(f"[ERROR] Falha na leitura do arquivo de referência local: {e}")
        return

    # 3. Transformação e Consolidação dos Dados (Merge)
    df_consolidado = pd.merge(df_mercado, df_bella, on="id_produto_interno", how="inner")
    df_consolidado["data_registro"] = pd.to_datetime(data_carga)
    
    # Padronização do esquema de colunas da tabela de destino
    colunas_ordenadas = [
        "data_registro", "id_produto_interno", "nome", 
        "categoria", "preco_bella_varejo", "preco_mercado_global"
    ]
    df_consolidado = df_consolidado[colunas_ordenadas]
    print("[INFO] Processo de unificação de esquemas concluído.")

    # 4. Carga de Dados no Data Warehouse (Google BigQuery - Camada Bronze)
    try:
        print("[INFO] Gravando partição de dados no Google BigQuery via streaming/append...")
        
        # Inicialização das credenciais de serviço do Google Cloud Platform
        credencial = service_account.Credentials.from_service_account_file(CAMINHO_CHAVE)
        
        # Escrita direta de Dataframe utilizando a biblioteca padrão recomendada
        pandas_gbq.to_gbq(
            dataframe=df_consolidado,
            destination_table=f"{DATASET_ID}.{TABLE_ID}",
            project_id=PROJECT_ID,
            credentials=credencial,
            if_exists="append" 
        )
        print(f"[SUCCESS] Partição persistida com sucesso na tabela: {DATASET_ID}.{TABLE_ID}")
        
    except Exception as e:
        print(f"[ERROR] Falha no processo de carga (Data Ingestion) para o Cloud DW: {e}")

# === Bloco de Execução do Pipeline ===
if __name__ == "__main__":
    print("[INFO] Inicializando carga diária incremental (Janela: Hoje)...")
    
    # Força a data para o horário de Brasília (UTC-3)
    fuso_brasilia = timezone(timedelta(hours=-3))
    data_final = datetime.now(fuso_brasilia)
    
    data_formatada = data_final.strftime("%Y-%m-%d")
    executar_pipeline_diario(data_formatada)
    
    print("\n[SUCCESS] Pipeline finalizado. Dados de hoje consolidados na nuvem.")