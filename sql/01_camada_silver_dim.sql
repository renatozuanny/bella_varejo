CREATE OR REPLACE VIEW `bella-varejo-analytics.silver_camada.dim_produtos` AS
SELECT DISTINCT
  id_produto_interno,
  nome,
  categoria
FROM
  `bella-varejo-analytics.bronze_camada.fato_pricing_mercado`;