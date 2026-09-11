FROM apache/airflow:3.3.1

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir \
    -r /tmp/requirements.txt

COPY ingestion/ /opt/airflow/urbanflow/ingestion/
COPY processing/ /opt/airflow/urbanflow/processing/
COPY utils/ /opt/airflow/urbanflow/utils/

ENV PYTHONPATH="/opt/airflow/urbanflow"