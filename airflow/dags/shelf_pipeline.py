from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="shelf_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:

    predict_task = BashOperator(
        task_id="predict_images",
        bash_command="python /opt/airflow/backend/src/pipeline/predict_batch.py"
    )

    insert_task = BashOperator(
        task_id="insert_predictions",
        bash_command="python /opt/airflow/backend/src/db/insert_predictions.py"
    )

    dbt_task = BashOperator(
        task_id="run_dbt",
        bash_command="cd /opt/airflow/dbt && dbt run"
    )

    predict_task >> insert_task >> dbt_task