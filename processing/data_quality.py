import logging

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from processing.process_gtfs import get_latest_gtfs, load_gtfs
from processing.spark_session import create_spark_session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("urbanflow")


IDENTIFIER_COLUMNS = {
    "routes": ["route_id"],
    "trips": ["trip_id", "route_id"],
    "stops": ["stop_id"],
    "stop_times": ["trip_id", "stop_id"],
    "calendar": ["service_id"],
}


def check_null_identifiers(dataframes: dict[str, DataFrame]) -> None:
    """Comprueba valores nulos en los identificadores principales."""
    logger.info("COMPROBANDO IDENTIFICADORES NULOS")

    for name, columns in IDENTIFIER_COLUMNS.items():
        dataframe = dataframes[name]

        for column in columns:
            null_count = dataframe.filter(F.col(column).isNull()).count()
            logger.info("%s.%s nulos: %d", name, column, null_count)


def check_duplicates(dataframes: dict[str, DataFrame]) -> None:
    """Comprueba registros duplicados."""
    logger.info("COMPROBANDO DUPLICADOS")

    for name, dataframe in dataframes.items():
        total_rows = dataframe.count()
        distinct_rows = dataframe.dropDuplicates().count()
        duplicate_rows = total_rows - distinct_rows

        logger.info("%s: %d registros duplicados", name, duplicate_rows)


def check_referential_integrity(dataframes: dict[str, DataFrame]) -> None:
    """Comprueba las relaciones principales entre tablas GTFS."""
    logger.info("COMPROBANDO INTEGRIDAD REFERENCIAL")

    routes = dataframes["routes"]
    trips = dataframes["trips"]
    stops = dataframes["stops"]
    stop_times = dataframes["stop_times"]

    invalid_routes = (
        trips.select("route_id")
        .distinct()
        .join(
            routes.select("route_id").distinct(),
            on="route_id",
            how="left_anti",
        )
        .count()
    )
    logger.info("trips.route_ids sin correspondencia: %d", invalid_routes)

    invalid_trips = (
        stop_times.select("trip_id")
        .distinct()
        .join(
            trips.select("trip_id").distinct(),
            on="trip_id",
            how="left_anti",
        )
        .count()
    )
    logger.info("stop_times.trip_ids sin correspondencia: %d", invalid_trips)

    invalid_stops = (
        stop_times.select("stop_id")
        .distinct()
        .join(
            stops.select("stop_id").distinct(),
            on="stop_id",
            how="left_anti",
        )
        .count()
    )
    logger.info("stop_times.stop_ids sin correspondencia: %d", invalid_stops)


def check_coordinates(dataframes: dict[str, DataFrame]) -> None:
    """Comprueba la calidad de las coordenadas de las paradas."""
    logger.info("COMPROBANDO COORDENADAS")

    stops = dataframes["stops"]

    missing_lat = stops.filter(F.col("stop_lat").isNull()).count()
    missing_lon = stops.filter(F.col("stop_lon").isNull()).count()

    invalid_coordinates = stops.filter(
        (F.col("stop_lat") < -90)
        | (F.col("stop_lat") > 90)
        | (F.col("stop_lon") < -180)
        | (F.col("stop_lon") > 180)
    ).count()

    logger.info("Paradas sin latitud: %d", missing_lat)
    logger.info("Paradas sin longitud: %d", missing_lon)
    logger.info("Coordenadas fuera de rango: %d", invalid_coordinates)


def main():
    logger.info("URBANFLOW - DATA QUALITY")
    spark = create_spark_session()

    try:
        gtfs_path = get_latest_gtfs()
        dataframes = load_gtfs(spark, gtfs_path)

        check_null_identifiers(dataframes)
        check_duplicates(dataframes)
        check_referential_integrity(dataframes)
        check_coordinates(dataframes)

        logger.info("DATA QUALITY COMPLETADA CORRECTAMENTE")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
