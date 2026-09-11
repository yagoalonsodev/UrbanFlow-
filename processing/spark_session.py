from pyspark.sql import SparkSession


def create_spark_session() -> SparkSession:
    """
    Crea la SparkSession de UrbanFlow.
    """

    spark = (
        SparkSession.builder
        .appName("UrbanFlow-GTFS-Processing")
        .master("local[*]")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    return spark


def main():
    spark = create_spark_session()

    print("SparkSession creada correctamente.")
    print(f"Spark version: {spark.version}")

    spark.stop()


if __name__ == "__main__":
    main()