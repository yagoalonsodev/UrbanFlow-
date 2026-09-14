import os


# TMB

TMB_REALTIME_URL = "https://api.tmb.cat/v1/ibus/stops"
TMB_BASE_URL = "https://api.tmb.cat/v1/static/datasets/gtfs.zip"

# Kafka

KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "localhost:9092",
)

KAFKA_TOPIC_GTFS_REALTIME = "gtfs-realtime"
KAFKA_TOPIC_TRANSPORT_ALERTS = "transport-alerts"
KAFKA_TOPIC_TRANSPORT_ERRORS = "transport-errors"


# PostgreSQL

POSTGRES_TABLE = "realtime_bus_arrivals"


# Streaming

STREAMING_INTERVAL_SECONDS = 30


# Spark

SPARK_KAFKA_PACKAGE = (
    "org.apache.spark:spark-sql-kafka-0-10_2.13:4.2.0"
)

POSTGRES_JDBC_PACKAGE = (
    "org.postgresql:postgresql:42.7.7"
)