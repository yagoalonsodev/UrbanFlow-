# TMB

TMB_REALTIME_URL = "https://api.tmb.cat/v1/ibus/stops"


# Kafka

KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
KAFKA_TOPIC_GTFS_REALTIME = "gtfs-realtime"


# PostgreSQL

POSTGRES_REALTIME_TABLE = "realtime_bus_arrivals"


# Streaming

STREAMING_INTERVAL_SECONDS = 30
STREAMING_CHECKPOINT = "/tmp/urbanflow-checkpoint-postgres"


# Spark

SPARK_KAFKA_PACKAGE = (
    "org.apache.spark:spark-sql-kafka-0-10_2.13:4.2.0"
)

POSTGRES_JDBC_PACKAGE = (
    "org.postgresql:postgresql:42.7.7"
)