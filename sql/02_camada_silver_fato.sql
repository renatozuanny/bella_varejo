CREATE OR REPLACE VIEW `bella-varejo-analytics.silver_camada.fato_precos_mercado` AS
WITH dados_ranqueados AS (
  SELECT
    DATE(data_registro) AS data_registro,
    id_produto_interno,
    preco_bella_varejo,
    preco_mercado_global,
    ROW_NUMBER() OVER(
      PARTITION BY DATE(data_registro), id_produto_interno 
      ORDER BY data_registro DESC
    ) AS linha_numero
  FROM 
    `bella-varejo-analytics.bronze_camada.fato_pricing_mercado`
)
SELECT
  data_registro,
  id_produto_interno,
  preco_bella_varejo,
  preco_mercado_global AS preco_mercado
FROM
  dados_ranqueados
WHERE
  linha_numero = 1;