from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    from_json,
    from_unixtime,
    trim,
)
from pyspark.sql.types import (
    IntegerType,
    LongType,
    StringType,
    StructField,
    StructType,
)

from utils.config import (
    POSTGRES_PASSWORD,
    POSTGRES_URL,
    POSTGRES_USER,
)
from utils.constants import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC_GTFS_REALTIME,
    POSTGRES_TABLE,
)


def create_spark_session():
    return (
        SparkSession.builder
        .appName("UrbanFlow-Streaming")
        .master("local[*]")
        .config(
            "spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.13:4.2.0,"
            "org.postgresql:postgresql:42.7.7",
        )
        .getOrCreate()
    )


def write_to_postgres(batch_df, batch_id):
    print()
    print("=" * 50)
    print(f"POSTGRESQL - BATCH {batch_id}")
    print("=" * 50)

    if batch_df.isEmpty():
        print("Batch vacío. No se insertan datos.")
        return

    rows = batch_df.count()

    print(f"Filas recibidas: {rows}")
    print(f"Tabla destino: {POSTGRES_TABLE}")

    (
        batch_df.write
        .format("jdbc")
        .option("url", POSTGRES_URL)
        .option("dbtable", POSTGRES_TABLE)
        .option("user", POSTGRES_USER)
        .option("password", POSTGRES_PASSWORD)
        .option("driver", "org.postgresql.Driver")
        .mode("append")
        .save()
    )

    print(f"Filas insertadas en PostgreSQL: {rows}")
    print("=" * 50)


def main():

    print("=" * 50)
    print("URBANFLOW - SPARK STRUCTURED STREAMING")
    print("=" * 50)

    if not POSTGRES_PASSWORD:
        raise RuntimeError(
            "No se ha encontrado POSTGRES_PASSWORD."
        )

    spark = create_spark_session()

    spark.sparkContext.setLogLevel("WARN")

    # Schema recibido desde Kafka

    schema = StructType([
        StructField("timestamp", LongType(), True),
        StructField("destination", StringType(), True),
        StructField("line", StringType(), True),
        StructField("route_id", StringType(), True),
        StructField("stop", StringType(), True),
        StructField("time_in_minutes", IntegerType(), True),
        StructField("time_in_seconds", IntegerType(), True),
        StructField("text_ca", StringType(), True),
    ])

    # Kafka

    raw_stream = (
        spark.readStream
        .format("kafka")
        .option(
            "kafka.bootstrap.servers",
            KAFKA_BOOTSTRAP_SERVERS,
        )
        .option(
            "subscribe",
            KAFKA_TOPIC_GTFS_REALTIME,
        )
        .option(
            "startingOffsets",
            "latest",
        )
        .option(
            "failOnDataLoss",
            "false",
        )
        .load()
    )

    # JSON

    json_stream = raw_stream.select(
        from_json(
            col("value").cast("string"),
            schema,
        ).alias("data")
    )

    parsed_stream = json_stream.select("data.*")

    # Limpieza y normalización

    clean_stream = (
        parsed_stream

        .withColumn(
            "destination",
            trim(col("destination")),
        )

        .withColumn(
            "line",
            trim(col("line")),
        )

        .withColumn(
            "route_id",
            trim(col("route_id")),
        )

        .withColumn(
            "stop_id",
            trim(col("stop")),
        )

        .withColumn(
            "arrival_text",
            trim(col("text_ca")),
        )

        .withColumnRenamed(
            "time_in_minutes",
            "arrival_minutes",
        )

        .withColumnRenamed(
            "time_in_seconds",
            "arrival_seconds",
        )

        .withColumn(
            "event_timestamp",
            from_unixtime(
                col("timestamp")
            ).cast("timestamp"),
        )

        .drop(
            "timestamp",
            "stop",
            "text_ca",
        )
    )

    # Orden final

    final_stream = clean_stream.select(
        "event_timestamp",
        "destination",
        "line",
        "route_id",
        "stop_id",
        "arrival_minutes",
        "arrival_seconds",
        "arrival_text",
    )

    final_stream = final_stream.filter(
        col("event_timestamp").isNotNull()
        & col("line").isNotNull()
        & col("route_id").isNotNull()
        & col("stop_id").isNotNull()
        & col("arrival_minutes").isNotNull()
        & col("arrival_seconds").isNotNull()
        & (col("arrival_minutes") >= 0)
        & (col("arrival_seconds") >= 0)
    )

    # Kafka → Spark → PostgreSQL

    query = (
        final_stream.writeStream
        .foreachBatch(write_to_postgres)
        .outputMode("append")
        .option(
            "checkpointLocation",
            "/tmp/urbanflow-checkpoint-postgres",
        )
        .start()
    )

    print()
    print("Spark Streaming iniciado.")
    print(f"Kafka: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Topic: {KAFKA_TOPIC_GTFS_REALTIME}")
    print(f"PostgreSQL: {POSTGRES_URL}")
    print(f"Tabla: {POSTGRES_TABLE}")
    print()
    print("Pipeline:")
    print("Kafka → Spark → limpieza → PostgreSQL")
    print()
    print("Esperando nuevos mensajes...")
    print()

    query.awaitTermination()


if __name__ == "__main__":
    main()