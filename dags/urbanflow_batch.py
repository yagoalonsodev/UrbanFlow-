from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


with DAG(
    dag_id="urbanflow_batch",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["urbanflow", "batch", "gtfs"],
) as dag:

    download_gtfs = BashOperator(
        task_id="download_gtfs",
        bash_command=(
            "set -e; "
            "python /opt/airflow/urbanflow/ingestion/download_gtfs.py"
        ),
    )

    validate_data = BashOperator(
        task_id="validate_data",
        bash_command=(
            "set -e; "
            "python /opt/airflow/urbanflow/ingestion/validate_data.py"
        ),
    )

    transform_gtfs = BashOperator(
        task_id="transform_gtfs",
        bash_command=(
            "set -e; "
            "python /opt/airflow/urbanflow/processing/transform_gtfs_spark.py"
        ),
    )

    upload_minio = BashOperator(
        task_id="upload_minio",
        bash_command=(
            "set -e; "
            "python /opt/airflow/urbanflow/processing/upload_minio.py"
        ),
    )

    load_postgres = BashOperator(
        task_id="load_postgres",
        bash_command=(
            "set -e; "
            "python /opt/airflow/urbanflow/processing/load_postgres.py"
        ),
    )

    (
        download_gtfs
        >> validate_data
        >> transform_gtfs
        >> upload_minio
        >> load_postgres
    )
