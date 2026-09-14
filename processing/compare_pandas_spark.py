import logging
import time

import pandas as pd
from pyspark.sql import functions as F

from processing.process_gtfs import get_latest_gtfs, load_gtfs
from processing.spark_session import create_spark_session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("urbanflow")


def compare_pandas(gtfs_path):
    """Procesar routes y trips utilizando Pandas."""
    start = time.perf_counter()

    routes = pd.read_csv(gtfs_path / "routes.txt", dtype=str)
    trips = pd.read_csv(gtfs_path / "trips.txt", dtype=str)

    routes = routes.drop_duplicates()
    trips = trips.drop_duplicates()

    route_trip_counts = (
        trips.groupby("route_id").size().reset_index(name="trip_count")
    )

    result = routes.merge(route_trip_counts, on="route_id", how="left")
    result["trip_count"] = result["trip_count"].fillna(0).astype(int)

    elapsed = time.perf_counter() - start
    return result, elapsed


def compare_spark(dataframes):
    """Procesar routes y trips utilizando PySpark."""
    start = time.perf_counter()

    routes = dataframes["routes"]
    trips = dataframes["trips"]

    routes = routes.dropDuplicates()
    trips = trips.dropDuplicates()

    route_trip_counts = trips.groupBy("route_id").count().withColumnRenamed(
        "count", "trip_count"
    )

    result = (
        routes.join(route_trip_counts, on="route_id", how="left")
        .fillna(0, subset=["trip_count"])
        .withColumn("trip_count", F.col("trip_count").cast("integer"))
    )

    result.cache()
    result.count()

    elapsed = time.perf_counter() - start
    return result, elapsed


def main():
    spark = create_spark_session()
    try:
        gtfs_path = get_latest_gtfs()
        logger.info("Comparando Pandas y PySpark...")

        pandas_result, pandas_time = compare_pandas(gtfs_path)

        dataframes = load_gtfs(spark, gtfs_path)
        spark_result, spark_time = compare_spark(dataframes)

        print("COMPARACIÓN PANDAS VS PYSPARK")
        print(
            f"\nPandas:"
            f"\nRutas: {len(pandas_result)}"
            f"\nTiempo: {pandas_time:.4f} segundos"
        )
        print(
            f"\nPySpark:"
            f"\nRutas: {spark_result.count()}"
            f"\nTiempo: {spark_time:.4f} segundos"
        )

        print("\nTop 10 rutas por número de viajes:")
        (
            spark_result.orderBy(F.col("trip_count").desc())
            .select("route_short_name", "trip_count")
            .show(10, truncate=False)
        )

        spark_result.unpersist()
        print("\nComparación completada correctamente.")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
