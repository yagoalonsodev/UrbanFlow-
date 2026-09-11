from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from ingestion.download_gtfs import main as download_gtfs
from ingestion.validate_data import main as validate_data
from processing.transform_gtfs_spark import main as transform_gtfs_spark
from processing.load_postgres import main as load_postgres


with DAG(
    dag_id="urbanflow_batch",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["urbanflow", "batch", "gtfs"],
) as dag:

    download_task = PythonOperator(
        task_id="download_gtfs",
        python_callable=download_gtfs,
    )

    validate_task = PythonOperator(
        task_id="validate_data",
        python_callable=validate_data,
    )

    transform_task = PythonOperator(
        task_id="transform_gtfs_spark",
        python_callable=transform_gtfs_spark,
    )

    load_task = PythonOperator(
        task_id="load_postgres",
        python_callable=load_postgres,
    )

    download_task >> validate_task >> transform_task >> load_task