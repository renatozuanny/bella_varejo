# %%
import pandas as pd
import random
import hashlib
from fastapi import FastAPI, HTTPException, Query
from datetime import date

# %%
app = FastAPI(
    title="API Mercado Geral - Simulador de Marketplace",
    description="API de preços da concorrência com consistência de dados baseada em semente temporal.",
    version="1.1.0"
)

NOME_ARQUIVO = "catalogo_bella_varejo.xlsx"

def gerar_semente_por_data(id_prod, data_str):
    """Gera um hash numérico determinístico baseado no ID do produto e na data alvo."""
    combinacao = f"{id_prod}_{data_str}"
    # Aplicação de hash MD5 para geração de uma semente numérica fixa
    return int(hashlib.md5(combinacao.encode()).hexdigest(), 16) % 1000000

def carregar_dados_mercado(data_alvo: str):
    """Processa a base de referência e aplica fatores determinísticos de oscilação baseados em data."""
    try:
        df = pd.read_excel(NOME_ARQUIVO)
        produtos_api = []
        
        for _, linha in df.iterrows():
            id_prod = str(linha['id_produto_interno'])
            preco_base = float(linha['preco_base_referencia'])
            
            # Inicialização da semente do gerador pseudo-aleatório para consistência diária
            semente = gerar_semente_por_data(id_prod, data_alvo)
            random.seed(semente)
            
            # Aplicação de fator de oscilação fixado para a janela temporal especificada (intervalo +/- 3%)
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
        raise RuntimeError(f"Erro no processamento da base local: {str(e)}")

@app.get("/")
def home():
    return {
        "status": "Operational",
        "service": "Mercado Geral API",
        "documentation": "Acesse /docs para a especificação completa das rotas ou /api/produtos para consumo direto."
    }

@app.get("/api/produtos")
def listar_produtos(data: str = Query(None, description="Formato aceito: AAAA-MM-DD. Caso nulo, adota a data corrente do servidor.")):
    try:
        # Fallback para a data atual caso o parâmetro de query esteja ausente
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
