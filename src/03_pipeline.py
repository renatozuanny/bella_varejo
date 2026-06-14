import pandas as pd
import requests
from datetime import datetime
from google.oauth2 import service_account

# Configurações de Origem
URL_API = "http://127.0.0.1:8000/api/produtos"
CAMINHO_EXCEL = "catalogo_bella_varejo.xlsx"

# Configurações do Google Cloud / BigQuery
PROJECT_ID = "bella-varejo-analytics"
DATASET_ID = "bronze_camada"      # Nome do nosso "banco" no BigQuery
TABLE_ID = "fato_pricing_mercado" # Nome da tabela bruta
CAMINHO_CHAVE = "credenciais_gcp.json"

def executar_pipeline_diario(data_carga: str):
    print(f"\n--- Iniciando Pipeline para a data: {data_carga} ---")
    
    # 1. Coleta os dados da API do Mercado Geral
    try:
        resposta = requests.get(URL_API, params={"data": data_carga})
        resposta.raise_for_status()
        dados_api = resposta.json()
        df_mercado = pd.DataFrame(dados_api["produtos"])
        df_mercado = df_mercado.rename(columns={
            "id_produto": "id_produto_interno",
            "preco_concorrente_mercado": "preco_mercado_global"
        })
        print(f"✓ Sucesso: {len(df_mercado)} produtos extraídos da API.")
    except Exception as e:
        print(f"❌ Erro ao conectar com a API: {e}")
        return

    # 2. Coleta os dados do seu Excel Local
    try:
        df_bella = pd.read_excel(CAMINHO_EXCEL)
        df_bella = df_bella[["id_produto_interno", "preco_bella_varejo"]]
        print(f"✓ Sucesso: Dados do catálogo local carregados.")
    except Exception as e:
        print(f"❌ Erro ao ler a planilha Excel: {e}")
        return

    # 3. Consolidação (Merge)
    df_consolidado = pd.merge(df_mercado, df_bella, on="id_produto_interno", how="inner")
    df_consolidado["data_registro"] = pd.to_datetime(data_carga)
    
    colunas_ordenadas = [
        "data_registro", "id_produto_interno", "nome", 
        "categoria", "preco_bella_varejo", "preco_mercado_global"
    ]
    df_consolidado = df_consolidado[colunas_ordenadas]
    print("✓ Sucesso: Dados de Pricing unificados.")

    # 4. CARGA NA NUVEM (BigQuery - Camada Bronze)
    try:
        print("⏳ Conectando e enviando dados para o Google BigQuery...")
        
        # Carrega a credencial do arquivo JSON
        credencial = service_account.Credentials.from_service_account_file(CAMINHO_CHAVE)
        
        # Envia o DataFrame direto para o BigQuery
        # Se a tabela não existir, o pandas cria na hora. Se existir, ele adiciona (append) os novos dados.
        df_consolidado.to_gbq(
            destination_table=f"{DATASET_ID}.{TABLE_ID}",
            project_id=PROJECT_ID,
            credentials=credencial,
            if_exists="append" 
        )
        print(f"🚀 SUCESSO ABSOLUTO! Dados carregados na tabela {DATASET_ID}.{TABLE_ID} no BigQuery.")
        
    except Exception as e:
        print(f"❌ Erro ao carregar dados no BigQuery: {e}")

# === ÁREA DE TESTE DE CARGA ===
# === ÁREA DE AUTOMAÇÃO DE HISTÓRICO (30 DIAS) ===
if __name__ == "__main__":
    from datetime import datetime, timedelta
    
    print("⏳ Iniciando carga de histórico de 30 dias...")
    
    # 1. Definimos a data final como o dia de hoje (12 de Junho de 2026)
    data_final = datetime.strptime("2026-06-12", "%Y-%m-%d")
    
    # 2. Criamos o loop para rodar 30 vezes voltando no tempo
    for i in range(30):
        # Subtrai 'i' dias da data final (0 dias atrás, 1 dia atrás, 2 dias atrás...)
        data_corrente = data_final - timedelta(days=i)
        
        # Transforma a data de volta para o formato de texto que a API espera
        data_formatada = data_corrente.strftime("%Y-%m-%d")
        
        # Dispara o pipeline para a data específica
        executar_pipeline_diario(data_formatada)
        
    print("\n🏆 PROCESSO CONCLUÍDO! 30 dias de dados foram empilhados com sucesso na nuvem!")