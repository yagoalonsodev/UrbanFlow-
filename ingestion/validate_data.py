import logging
from pathlib import Path

import pandas as pd

from utils.config import TMB_RAW_DIR


logger = logging.getLogger(__name__) # aqui se guardan los logs de la app.


# Archivos GTFS obligatorios
REQUIRED_FILES = {
    "agency.txt",
    "stops.txt",
    "routes.txt",
    "trips.txt",
    "stop_times.txt",
    "calendar.txt",
}


# Columnas obligatorias de cada archivo
REQUIRED_COLUMNS = {
    "agency.txt": {
        "agency_name",
        "agency_url",
        "agency_timezone",
        "agency_lang",
        "agency_phone",
    },
    "stops.txt": {
        "stop_id",
        "stop_code",
        "stop_name",
        "stop_lat",
        "stop_lon",
        "stop_url",
        "location_type",
        "parent_station",
        "wheelchair_boarding",
    },
    "routes.txt": {
        "route_id",
        "route_short_name",
        "route_long_name",
        "route_type",
        "route_url",
        "route_color",
        "route_text_color",
    },
    "trips.txt": {
        "route_id",
        "service_id",
        "trip_id",
        "trip_headsign",
        "direction_id",
        "shape_id",
        "wheelchair_accessible",
    },
    "stop_times.txt": {
        "trip_id",
        "arrival_time",
        "departure_time",
        "stop_id",
        "stop_sequence",
    },
    "calendar.txt": {
        "service_id",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
        "start_date",
        "end_date",
    },
}


def get_latest_gtfs_directory() -> Path:
    """
    Buscamos la carpeta GTFS más reciente.
    """

    gtfs_directories = [
        directory
        for directory in TMB_RAW_DIR.iterdir()
        if directory.is_dir()
    ]

    if not gtfs_directories:
        raise FileNotFoundError(
            "No se ha encontrado ninguna carpeta GTFS."
        )

    latest_directory = sorted(gtfs_directories)[-1]

    extracted_directory = latest_directory / "extracted"

    if not extracted_directory.exists():
        raise FileNotFoundError(
            "No se ha encontrado la carpeta extracted."
        )

    logger.info(
        "Utilizando GTFS: %s",
        extracted_directory,
    )

    return extracted_directory


def validate_files(gtfs_directory: Path) -> None:
    """
    Comprobamos que existen los archivos GTFS obligatorios.
    """

    logger.info("Comprobando archivos GTFS...")

    missing_files = {
        file
        for file in REQUIRED_FILES
        if not (gtfs_directory / file).exists()
    }

    if missing_files:
        raise ValueError(
            f"Faltan archivos GTFS obligatorios: {missing_files}"
        )

    logger.info("Todos los archivos GTFS obligatorios existen.")


def validate_columns(gtfs_directory: Path) -> None:
    """
    Comprobamos que los archivos contienen las columnas necesarias.
    """

    logger.info("Comprobando columnas GTFS...")

    for file_name, required_columns in REQUIRED_COLUMNS.items():

        file_path = gtfs_directory / file_name

        dataframe = pd.read_csv(
            file_path,
            nrows=5,
        )

        columns = set(dataframe.columns)

        missing_columns = required_columns - columns

        if missing_columns:
            raise ValueError(
                f"{file_name} no contiene las columnas obligatorias: "
                f"{missing_columns}"
            )

        logger.info(
            "%s: columnas correctas.",
            file_name,
        )

    logger.info("Validación de columnas completada correctamente.")


def validate_records(gtfs_directory: Path) -> None:
    """
    Comprobamos que los archivos contienen registros.
    """

    logger.info("Comprobando registros GTFS...")

    for file_name in REQUIRED_FILES:

        file_path = gtfs_directory / file_name

        dataframe = pd.read_csv(file_path)

        records = len(dataframe)

        if records == 0:
            raise ValueError(
                f"{file_name} no contiene registros."
            )

        logger.info(
            "%s: %d registros.",
            file_name,
            records,
        )

    logger.info("Validación de registros completada correctamente.")


def main():
    logger.info("URBANFLOW BARCELONA - GTFS DATA VALIDATION")

    try:
        gtfs_directory = get_latest_gtfs_directory()

        validate_files(gtfs_directory)
        validate_columns(gtfs_directory)
        validate_records(gtfs_directory)

        logger.info(
            "VALIDACIÓN DE DATOS COMPLETADA CORRECTAMENTE"
        )

    except (OSError, ValueError) as error:
        logger.error(
            "Error validando los datos GTFS: %s",
            error,
        )
        raise

if __name__ == "__main__":
    main()