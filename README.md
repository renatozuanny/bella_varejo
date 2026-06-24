# Projeto Bella Varejo: Automação de Pricing e Analytics

## Visão Geral

O **Bella Varejo** é um projeto de engenharia de dados *end-to-end* desenvolvido para automatizar o monitoramento de precificação e conformidade de SKUs. O objetivo é transformar dados brutos em decisões estratégicas, reduzindo drasticamente o tempo operacional de análise.

## 📸 Evidências do Projeto

|                   Orquestração (Airflow)                   |                         Dashboard (Power BI)                         |
| :----------------------------------------------------------: | :-------------------------------------------------------------------: |
| ![Log Airflow](assets/screenshots/Airflow_log_23.06.2026.jpeg) | ![Dashboard](assets/screenshots/Dashboard_Bella_Varejo_24.06.2026.jpeg) |

## 🏗️ Arquitetura e Engenharia

* **Arquitetura Medallion:** Pipeline organizado em camadas (Bronze, Silver e Gold) para garantir governança e qualidade dos dados.
* **Orquestração:** Apache Airflow (via Astronomer) automatizando a carga incremental diária.
* **Processamento:** Python (`Pandas`) para consumo de API com tratamento de erros.
* **Data Warehouse:** Google BigQuery (modelo *Star Schema*).
* **Visualização:** Power BI (UI/UX focado em detecção de desvios de preço).


## 🗺️ Fluxo do Pipeline (Arquitetura)

1. **Extração:** API Externa → **Apache Airflow** (Orquestração).
2. **Bronze:** Carga bruta no **Google BigQuery**.
3. **Silver:** Tratamento e modelagem (Criação de *Views* DIM e Fato).
4. **Gold:** Regras de negócio aplicadas (Criação de *View* final de consumo).
5. **Visualização:** **Power BI**.

## 📊 Principais KPIs do Projeto

* **% Conformidade:** Percentual de SKUs com preços dentro da faixa aceitável de mercado.
* **SKUs em Alerta:** Quantidade de produtos que apresentam desvios críticos e precisam de ação imediata.
* **Desvio Médio Geral:** Diferença média percentual entre o preço praticado pela loja e o preço de mercado.

## 🚀 Impacto no Negócio

* **Eficiência:** Eliminação de processos manuais, permitindo foco em análise estratégica.
* **Monitoramento:** Identificação automática de SKUs fora da conformidade de mercado.
* **Escalabilidade:** Arquitetura pronta para suportar o crescimento do volume de SKUs com o padrão Medallion.

## 🛠️ Tecnologias

`Python (Pandas/Requests)`, `Apache Airflow`, `SQL`, `Google BigQuery`, `Power BI`, `Docker`.
