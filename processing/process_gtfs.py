import logging
from pathlib import Path

from pyspark.sql import DataFrame

from processing.spark_session import create_spark_session


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("urbanflow")


BASE_DIR = Path("/app")

TMB_RAW_DIR = BASE_DIR / "data" / "raw" / "tmb"


def get_latest_gtfs() -> Path:
    """
    Busca la versión más reciente del GTFS descargado.
    """

    gtfs_dirs = [
        directory
        for directory in TMB_RAW_DIR.iterdir()
        if directory.is_dir()
        and (directory / "extracted").exists()
    ]

    if not gtfs_dirs:
        raise FileNotFoundError(
            "No se ha encontrado ningún GTFS descargado."
        )

    latest_dir = max(
        gtfs_dirs,
        key=lambda directory: directory.name,
    )

    return latest_dir / "extracted"


def load_gtfs(
    spark,
    gtfs_path: Path,
) -> dict[str, DataFrame]:
    """
    Carga los principales archivos GTFS como Spark DataFrames.
    """

    logger.info(
        "Cargando GTFS con PySpark: %s",
        gtfs_path,
    )

    files = {
    "agency": "agency.txt",
    "routes": "routes.txt",
    "trips": "trips.txt",
    "stops": "stops.txt",
    "stop_times": "stop_times.txt",
    "calendar": "calendar.txt",
    "calendar_dates": "calendar_dates.txt",
}
    dataframes = {}

    for name, filename in files.items():

        file_path = gtfs_path / filename

        dataframe = (
            spark.read
            .option("header", True)
            .option("inferSchema", True)
            .csv(str(file_path))
        )

        dataframes[name] = dataframe

        logger.info(
            "%s cargado correctamente: %d registros",
            filename,
            dataframe.count(),
        )

    return dataframes


def main():
    spark = create_spark_session()

    try:
        gtfs_path = get_latest_gtfs()

        dataframes = load_gtfs(
            spark,
            gtfs_path,
        )

        logger.info(
            "GTFS cargado correctamente con PySpark."
        )

        for name, dataframe in dataframes.items():

            print(f"\n===== {name} =====")

            dataframe.printSchema()

            print(
                f"Registros: {dataframe.count()}"
            )

            dataframe.show(
                5,
                truncate=False,
            )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()