import pandas as pd
import requests
from datetime import datetime
from google.oauth2 import service_account

# Parâmetros de Origem e Consumo de API
URL_API = "http://127.0.0.1:8000/api/produtos"
CAMINHO_EXCEL = "catalogo_bella_varejo.xlsx"

# Parâmetros de Destino - Cloud Data Warehouse (Google BigQuery)
PROJECT_ID = "bella-varejo-analytics"
DATASET_ID = "bronze_camada"      # Schema/Dataset destino no BigQuery
TABLE_ID = "fato_pricing_mercado" # Tabela fato bruta de destino
CAMINHO_CHAVE = "credenciais_gcp.json"

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
        
        # Escrita direta de Dataframe no BigQuery utilizando método Append
        df_consolidado.to_gbq(
            destination_table=f"{DATASET_ID}.{TABLE_ID}",
            project_id=PROJECT_ID,
            credentials=credencial,
            if_exists="append" 
        )
        print(f"[SUCCESS] Partição persistida com sucesso na tabela: {DATASET_ID}.{TABLE_ID}")
        
    except Exception as e:
        print(f"[ERROR] Falha no processo de carga (Data Ingestion) para o Cloud DW: {e}")

# === Bloco de Execução de Histórico ===
if __name__ == "__main__":
    from datetime import datetime, timedelta
    
    print("[INFO] Inicializando carga histórica retroativa (Janela: 30 dias)...")
    
    # Definição do ponto de partida cronológico para processamento em lote
    data_final = datetime.strptime("2026-06-12", "%Y-%m-%d")
    
    # Loop de processamento em lote retroativo
    for i in range(30):
        data_corrente = data_final - timedelta(days=i)
        data_formatada = data_corrente.strftime("%Y-%m-%d")
        
        # Execução incremental diária
        executar_pipeline_diario(data_formatada)
        
    print("\n[SUCCESS] Pipeline finalizado. Carga histórica de 30 dias executada e consolidada na nuvem.")