from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# Configurações padrão da DAG (Metadados e regras de reexecução)
default_args = {
    'owner': 'Renato Carvalho',
    'depends_on_past': False,
    'start_date': datetime(2026, 6, 1),  # Começa a contar a partir de Junho de 2026
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Definição do escopo da nossa DAG
with DAG(
    'pipeline_bella_varejo_diario',
    default_args=default_args,
    description='Automação diária do pipeline de dados da Bella Varejo',
    schedule='0 6 * * *',  # Expressão Cron: Executa todos os dias às 06:00 da manhã
    catchup=False,
    tags=['bella_varejo', 'ingestion'],
) as dag:

    # A tarefa que o Airflow vai gerenciar
    executar_pipeline = BashOperator(
        task_id='executar_script_pipeline',
        # Aponta exatamente para onde o Docker mapeia a sua pasta local de scripts
        bash_command='python /usr/local/airflow/src/03_pipeline.py',
    )

    # Define a ordem de execução (como só temos uma tarefa, ela fica sozinha)
    executar_pipeline