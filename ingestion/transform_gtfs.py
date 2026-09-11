import logging
from pathlib import Path

import pandas as pd

from utils.config import TMB_PROCESSED_DIR, TMB_RAW_DIR


logger = logging.getLogger(__name__)


def get_latest_gtfs() -> Path:
    """
    Buscamos la carpeta GTFS más reciente.
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


def load_gtfs(gtfs_path: Path) -> dict[str, pd.DataFrame]:
    """
    Cargamos los archivos GTFS en DataFrames.
    """

    logger.info("Cargando archivos GTFS...")

    files = {
        "agency": "agency.txt",
        "routes": "routes.txt",
        "trips": "trips.txt",
        "stops": "stops.txt",
        "stop_times": "stop_times.txt",
        "calendar": "calendar.txt",
    }

    dataframes = {}

    for name, filename in files.items():

        file_path = gtfs_path / filename

        dataframes[name] = pd.read_csv(
            file_path,
            dtype=str,
        )

        logger.info(
            "%s cargado correctamente: %d registros",
            filename,
            len(dataframes[name]),
        )

    return dataframes


def transform_gtfs(
    dataframes: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """
    Transformamos y limpiamos los datos GTFS.
    """

    logger.info("Iniciando transformaciones...")

    # Copiamos los DataFrames para no modificar los datos Raw

    transformed = {
        name: dataframe.copy()
        for name, dataframe in dataframes.items()
    }

    # Eliminamos espacios innecesarios de los nombres de columnas

    for dataframe in transformed.values():

        dataframe.columns = (
            dataframe.columns
            .str.strip()
        )

    # Normalizamos valores de texto y convertimos cadenas vacías a nulos

    for dataframe in transformed.values():

        object_columns = dataframe.select_dtypes(
            include=["object", "string"]
        ).columns

        for column in object_columns:

            dataframe[column] = (
                dataframe[column]
                .str.strip()
                .replace("", pd.NA)
            )

    # Convertimos coordenadas a valores numéricos

    stops = transformed["stops"]

    stops["stop_lat"] = pd.to_numeric(
        stops["stop_lat"],
        errors="coerce",
    )

    stops["stop_lon"] = pd.to_numeric(
        stops["stop_lon"],
        errors="coerce",
    )

    # Convertimos stop_sequence a número

    stop_times = transformed["stop_times"]

    stop_times["stop_sequence"] = pd.to_numeric(
        stop_times["stop_sequence"],
        errors="coerce",
    )

    # Eliminamos registros completamente duplicados

    for name, dataframe in transformed.items():

        before = len(dataframe)

        transformed[name] = dataframe.drop_duplicates()

        after = len(transformed[name])

        logger.info(
            "%s: %d duplicados eliminados",
            name,
            before - after,
        )

    # Eliminamos stop_id duplicados manteniendo el primer registro

    stops = transformed["stops"]

    before = len(stops)

    stops = stops.drop_duplicates(
        subset=["stop_id"],
        keep="first",
    )

    transformed["stops"] = stops

    logger.info(
        "stops: %d stop_id duplicados eliminados",
        before - len(stops),
    )

    # Eliminamos registros sin identificadores principales

    for name, dataframe in transformed.items():

        identifier_columns = []

        if name == "routes":
            identifier_columns = ["route_id"]

        elif name == "trips":
            identifier_columns = ["trip_id"]

        elif name == "stops":
            identifier_columns = ["stop_id"]

        elif name == "stop_times":
            identifier_columns = [
                "trip_id",
                "stop_id",
            ]

        elif name == "calendar":
            identifier_columns = ["service_id"]

        if identifier_columns:

            before = len(dataframe)

            dataframe = dataframe.dropna(
                subset=identifier_columns,
            )

            transformed[name] = dataframe

            logger.info(
                "%s: %d registros sin identificadores eliminados",
                name,
                before - len(dataframe),
            )

    # Eliminamos paradas sin coordenadas

    stops = transformed["stops"]

    before = len(stops)

    stops = stops.dropna(
        subset=[
            "stop_lat",
            "stop_lon",
        ],
    )

    transformed["stops"] = stops

    logger.info(
        "stops: %d registros sin coordenadas eliminados",
        before - len(stops),
    )

    logger.info(
        "Transformaciones completadas correctamente."
    )

    return transformed


def save_processed_data(
    dataframes: dict[str, pd.DataFrame],
    date: str,
) -> None:
    """
    Guardamos los datos transformados en Processed.
    """

    output_dir = TMB_PROCESSED_DIR / date

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger.info(
        "Guardando datos transformados en: %s",
        output_dir,
    )

    for name, dataframe in dataframes.items():

        output_file = output_dir / f"{name}.csv"

        dataframe.to_csv(
            output_file,
            index=False,
        )

        logger.info(
            "%s guardado: %d registros",
            output_file,
            len(dataframe),
        )


def analyze_final_data(
    dataframes: dict[str, pd.DataFrame],
) -> None:
    """
    Comprobamos el estado final de los datos transformados.
    """

    logger.info("ANÁLISIS FINAL DE LOS DATOS")

    for name, dataframe in dataframes.items():

        logger.info("%s", name)

        # Número de registros

        logger.info(
            "Registros finales: %d",
            len(dataframe),
        )

        # Valores nulos

        null_values = dataframe.isna().sum()

        total_nulls = null_values.sum()

        logger.info(
            "Valores nulos finales: %d",
            total_nulls,
        )

        # Registros duplicados

        duplicated_rows = dataframe.duplicated().sum()

        logger.info(
            "Registros duplicados finales: %d",
            duplicated_rows,
        )

    # Comprobamos los stop_id duplicados

    stops = dataframes["stops"]

    duplicate_stop_ids = (
        stops["stop_id"]
        .duplicated()
        .sum()
    )

    logger.info(
        "stop_id duplicados finales: %d",
        duplicate_stop_ids,
    )

    logger.info(
        "ANÁLISIS FINAL COMPLETADO CORRECTAMENTE"
    )


def main():
    try:

        gtfs_path = get_latest_gtfs()

        dataframes = load_gtfs(
            gtfs_path
        )

        transformed_data = transform_gtfs(
            dataframes
        )

        date = gtfs_path.parent.name

        save_processed_data(
            transformed_data,
            date,
        )

        analyze_final_data(
            transformed_data
        )

        logger.info(
            "TRANSFORMACIÓN GTFS COMPLETADA CORRECTAMENTE"
        )

    except (OSError, ValueError, KeyError) as error:

        logger.error(
            "Error durante la transformación del GTFS: %s",
            error,
        )

        raise


if __name__ == "__main__":
    main()
