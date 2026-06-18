WITH dados_base AS (
  SELECT
    f.data_registro,
    f.id_produto_interno,
    d.nome AS nome_produto,
    d.categoria,
    f.preco_bella_varejo,
    f.preco_mercado,
    (f.preco_bella_varejo - f.preco_mercado) AS diferenca_reais,
    ROUND(f.preco_bella_varejo / f.preco_mercado, 4) AS indice_competitividade,
    -- Regra de Negócio Precisa: Metas de Tolerância por Categoria conforme o mercado
    CASE 
      WHEN d.categoria = 'Smartphone' THEN 0.02
      WHEN d.categoria = 'Notebook'   THEN 0.03
      WHEN d.categoria = 'TV'         THEN 0.04
      WHEN d.categoria = 'Geladeira'  THEN 0.05
      WHEN d.categoria = 'Air Fryer'  THEN 0.07
      ELSE 0.05 -- Segurança para caso entre uma categoria nova no futuro
    END AS margem_tolerancia
  FROM
    `bella-varejo-analytics.silver_camada.fato_precos_mercado` f
  INNER JOIN
    `bella-varejo-analytics.silver_camada.dim_produtos` d 
    ON f.id_produto_interno = d.id_produto_interno
)
SELECT
  *,
  -- O farol evoluído para 5 níveis dinâmicos proporcionais à margem de cada categoria
  CASE 
    -- 1. CRITÉRIOS PARA MAIS (CARO)
    WHEN indice_competitividade > (1 + (margem_tolerancia * 2)) THEN 'Muito Caro (Fora da Meta)'
    WHEN indice_competitividade > (1 + margem_tolerancia)       THEN 'Pouco Caro (Alerta)'
    
    -- 2. CRITÉRIOS PARA MENOS (BARATO)
    WHEN indice_competitividade < (1 - (margem_tolerancia * 2)) THEN 'Muito Barato (Margem em Risco)'
    WHEN indice_competitividade < (1 - margem_tolerancia)       THEN 'Pouco Barato (Alerta)'
    
    -- 3. DENTRO DA MARGEM ACEITÁVEL
    ELSE 'No Alvo (Competitivo)'
  END AS status_farol_pricing
FROM
  dados_base