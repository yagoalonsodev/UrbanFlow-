import logging

from pyspark.sql import functions as F

from processing.process_gtfs import (
    get_latest_gtfs,
    load_gtfs,
)
from processing.spark_session import create_spark_session
from utils.config import (
    TMB_PROCESSED_DIR,
    TMB_RAW_DIR,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("urbanflow")


def get_latest_snapshot_date() -> str:
    """Obtiene la fecha del último snapshot GTFS."""

    snapshot_dirs = [
        directory
        for directory in TMB_RAW_DIR.iterdir()
        if directory.is_dir()
        and directory.name[:4].isdigit()
        and directory.name[4] == "-"
    ]

    if not snapshot_dirs:
        raise FileNotFoundError(
            f"No se encontraron snapshots GTFS en {TMB_RAW_DIR}"
        )

    latest_snapshot = max(
        snapshot_dirs,
        key=lambda directory: directory.name,
    )

    return latest_snapshot.name


def transform_routes(df):
    return (
        df
        .dropDuplicates()
        .withColumn(
            "route_id",
            F.col("route_id").cast("string"),
        )
        .withColumn(
            "route_short_name",
            F.trim(F.col("route_short_name")),
        )
        .withColumn(
            "route_long_name",
            F.trim(F.col("route_long_name")),
        )
        .withColumn(
            "route_type",
            F.col("route_type").cast("integer"),
        )
    )


def transform_trips(df):
    return (
        df
        .dropDuplicates()
        .withColumn(
            "route_id",
            F.col("route_id").cast("string"),
        )
        .withColumn(
            "service_id",
            F.col("service_id").cast("string"),
        )
        .withColumn(
            "trip_id",
            F.col("trip_id").cast("string"),
        )
        .withColumn(
            "trip_headsign",
            F.trim(F.col("trip_headsign")),
        )
        .withColumn(
            "direction_id",
            F.col("direction_id").cast("integer"),
        )
    )


def transform_stops(df):
    return (
        df
        .dropDuplicates()
        .withColumn(
            "stop_id",
            F.col("stop_id").cast("string"),
        )
        .withColumn(
            "stop_code",
            F.col("stop_code").cast("string"),
        )
        .withColumn(
            "stop_name",
            F.trim(F.col("stop_name")),
        )
        .withColumn(
            "stop_lat",
            F.col("stop_lat").cast("double"),
        )
        .withColumn(
            "stop_lon",
            F.col("stop_lon").cast("double"),
        )
        .filter(
            F.col("stop_id").isNotNull()
        )
        .filter(
            F.col("stop_lat").isNotNull()
            & F.col("stop_lon").isNotNull()
        )
    )


def transform_stop_times(df):
    return (
        df
        .dropDuplicates()
        .withColumn(
            "trip_id",
            F.col("trip_id").cast("string"),
        )
        .withColumn(
            "stop_id",
            F.col("stop_id").cast("string"),
        )
        .withColumn(
            "stop_sequence",
            F.col("stop_sequence").cast("integer"),
        )
        .withColumn(
            "arrival_time",
            F.trim(F.col("arrival_time")),
        )
        .withColumn(
            "departure_time",
            F.trim(F.col("departure_time")),
        )
        .filter(
            F.col("trip_id").isNotNull()
        )
        .filter(
            F.col("stop_id").isNotNull()
        )
    )


def transform_calendar(df):
    return (
        df
        .dropDuplicates()
        .withColumn(
            "service_id",
            F.col("service_id").cast("string"),
        )
        .withColumn(
            "start_date",
            F.to_date(
                F.col("start_date").cast("string"),
                "yyyyMMdd",
            ),
        )
        .withColumn(
            "end_date",
            F.to_date(
                F.col("end_date").cast("string"),
                "yyyyMMdd",
            ),
        )
    )


def transform_calendar_dates(df):
    return (
        df
        .dropDuplicates()
        .withColumn(
            "service_id",
            F.col("service_id").cast("string"),
        )
        .withColumn(
            "date",
            F.to_date(
                F.col("date").cast("string"),
                "yyyyMMdd",
            ),
        )
        .withColumn(
            "exception_type",
            F.col("exception_type").cast("integer"),
        )
    )


def transform_dataframes(dataframes):

    return {
        "agency": dataframes["agency"].dropDuplicates(),

        "routes": transform_routes(
            dataframes["routes"]
        ),

        "trips": transform_trips(
            dataframes["trips"]
        ),

        "stops": transform_stops(
            dataframes["stops"]
        ),

        "stop_times": transform_stop_times(
            dataframes["stop_times"]
        ),

        "calendar": transform_calendar(
            dataframes["calendar"]
        ),

        "calendar_dates": transform_calendar_dates(
            dataframes["calendar_dates"]
        ),
    }


def save_processed(

    dataframes,

    snapshot_date: str,

):

    """Guarda los datos procesados en formato Parquet."""

    year = snapshot_date[:4]

    month = snapshot_date[5:7]

    day = snapshot_date[8:10]

    processed_dir = (

        TMB_PROCESSED_DIR

        / f"year={year}"

        / f"month={month}"

        / f"day={day}"

    )

    processed_dir.mkdir(

        parents=True,

        exist_ok=True,

    )

    logger.info(

        "Guardando datos procesados en: %s",

        processed_dir,

    )

    for name, dataframe in dataframes.items():

        output_path = processed_dir / name

        (

            dataframe

            .write

            .mode("overwrite")

            .parquet(str(output_path))

        )

        logger.info(

            "%s guardado correctamente en formato Parquet.",

            name,

        )
def main():

    spark = create_spark_session()

    try:

        gtfs_path = get_latest_gtfs()

        snapshot_date = get_latest_snapshot_date()

        logger.info(
            "Snapshot GTFS seleccionado: %s",
            snapshot_date,
        )

        dataframes = load_gtfs(
            spark,
            gtfs_path,
        )

        logger.info(
            "Aplicando transformaciones..."
        )

        transformed = transform_dataframes(
            dataframes
        )

        save_processed(
            transformed,
            snapshot_date,
        )

        logger.info(
            "PROCESAMIENTO COMPLETADO CORRECTAMENTE"
        )

    finally:

        spark.stop()


if __name__ == "__main__":
    main()