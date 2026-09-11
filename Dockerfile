FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        openjdk-21-jre-headless \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ingestion/ ./ingestion/
COPY processing/ ./processing/
COPY streaming/ ./streaming/
COPY utils/ ./utils/

CMD ["python", "-m", "ingestion.download_gtfs"]