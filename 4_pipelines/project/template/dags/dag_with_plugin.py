from airflow import DAG
from datetime import datetime
from operators import PrintMessageOperator

default_args = {
    'start_date': datetime(2023, 7, 1),
    'retries': 1,
    # 'retry_delay': timedelta(minutes=5),
}

with DAG('example_custom_operator_dag', default_args=default_args, schedule_interval='@daily') as dag:
    task_print_message = PrintMessageOperator(
        task_id='print_message',
        message='Hello from the custom operator!',
    )
