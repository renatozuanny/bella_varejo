# %%
import pandas as pd
import random
import hashlib
from fastapi import FastAPI, HTTPException, Query
from datetime import date

# %%
app = FastAPI(
    title="API Mercado Geral - Simulador de Marketplace",
    description="API de preços da concorrência travada por data para consistência de dados.",
    version="1.1.0"
)

NOME_ARQUIVO = "catalogo_bella_varejo.xlsx"

def gerar_semente_por_data(id_prod, data_str):
    """Gera um número inteiro único baseado no ID do produto e na data."""
    combinacao = f"{id_prod}_{data_str}"
    # Usa criptografia simples (MD5) para transformar o texto em um número fixo
    return int(hashlib.md5(combinacao.encode()).hexdigest(), 16) % 1000000

def carregar_dados_mercado(data_alvo: str):
    """Lê a planilha e gera preços que só mudam quando a data muda."""
    try:
        df = pd.read_excel(NOME_ARQUIVO)
        produtos_api = []
        
        for _, linha in df.iterrows():
            id_prod = str(linha['id_produto_interno'])
            preco_base = float(linha['preco_base_referencia'])
            
            # Cria uma semente estável para o gerador aleatório usando a data e o ID
            semente = gerar_semente_por_data(id_prod, data_alvo)
            random.seed(semente)
            
            # A oscilação agora é fixa para este produto nesta data específica
            fator_oscilacao = random.uniform(0.97, 1.03)
            preco_concorrente = round(preco_base * fator_oscilacao, 2)
            
            produtos_api.append({
                "id_produto": id_prod,
                "nome": str(linha['nome_produto']),
                "categoria": str(linha['categoria']),
                "preco_concorrente_mercado": preco_concorrente
            })
            
        return produtos_api
    except Exception as e:
        raise RuntimeError(f"Erro ao processar a planilha: {str(e)}")

@app.get("/")
def home():
    return {
        "status": "Online",
        "mensagem": "Acesse /api/produtos para ver os preços estáveis do dia."
    }

@app.get("/api/produtos")
def listar_produtos(data: str = Query(None, description="Formato: AAAA-MM-DD. Se omitido, usa a data de hoje.")):
    try:
        # Se você não passar data no link, a API pega o dia de hoje automaticamente
        if not data:
            data = str(date.today())
            
        dados = carregar_dados_mercado(data)
        return {
            "data_da_consulta": data,
            "total_produtos": len(dados),
            "provedor": "Mercado Geral API Corporation",
            "produtos": dados
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
