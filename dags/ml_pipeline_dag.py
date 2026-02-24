from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# Default arguments for the DAG
default_args = {
    'owner': 'mlops_admin',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'mlops_weather_prediction_dag',
    default_args=default_args,
    description='Automated pipeline for pulling weather data and training model via DVC',
    schedule_interval=timedelta(days=1),
    catchup=False
)

# Task 1: Fetch raw data
task_fetch_data = BashOperator(
    task_id='fetch_weather_data',
    # Adjust python path if necessary depending on Airflow installation
    bash_command='python src/data_ingestion.py',
    cwd='/opt/airflow' if '/opt/airflow' in __file__ else 'd:/mlops-project', # Fallback to local
    dag=dag,
)

# Task 2: DVC run pipeline (Preprocessing & Training)
task_dvc_repro = BashOperator(
    task_id='dvc_repro',
    bash_command='dvc repro',
    cwd='/opt/airflow' if '/opt/airflow' in __file__ else 'd:/mlops-project',
    dag=dag,
)

# Task 3: DVC add (track raw data)
task_dvc_add = BashOperator(
    task_id='dvc_add',
    bash_command='dvc add data/raw',
    cwd='/opt/airflow' if '/opt/airflow' in __file__ else 'd:/mlops-project',
    dag=dag,
)

# Define dependencies
task_fetch_data >> task_dvc_repro >> task_dvc_add