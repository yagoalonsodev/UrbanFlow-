import logging
from pathlib import Path

import pandas as pd

from utils.config import TMB_RAW_DIR


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


def analyze_gtfs(gtfs_path: Path) -> None:
    """
    Analizamos los principales archivos del GTFS.
    """

    logger.info("URBANFLOW BARCELONA - GTFS DATA ANALYSIS")
    logger.info("Utilizando GTFS: %s", gtfs_path)

    # Cargamos los principales archivos GTFS

    agency = pd.read_csv(
        gtfs_path / "agency.txt",
        dtype=str,
    )

    routes = pd.read_csv(
        gtfs_path / "routes.txt",
        dtype=str,
    )

    trips = pd.read_csv(
        gtfs_path / "trips.txt",
        dtype=str,
    )

    stops = pd.read_csv(
        gtfs_path / "stops.txt",
        dtype=str,
    )

    stop_times = pd.read_csv(
        gtfs_path / "stop_times.txt",
        dtype=str,
    )

    calendar = pd.read_csv(
        gtfs_path / "calendar.txt",
        dtype=str,
    )

    important_files = {
        "agency.txt": agency,
        "routes.txt": routes,
        "trips.txt": trips,
        "stops.txt": stops,
        "stop_times.txt": stop_times,
        "calendar.txt": calendar,
    }

    # Análisis inicial de los datos

    logger.info("ANÁLISIS INICIAL DE LOS DATOS")

    for filename, dataframe in important_files.items():

        logger.info("%s", filename)

        # Mostramos los primeros 5 registros

        logger.info(
            "Primeros 5 registros:\n%s",
            dataframe.head(5).to_string(index=False),
        )

        # Mostramos las dimensiones del archivo

        logger.info(
            "Filas: %d | Columnas: %d",
            dataframe.shape[0],
            dataframe.shape[1],
        )

        # Mostramos los tipos de datos

        logger.info(
            "Tipos de datos:\n%s",
            dataframe.dtypes.to_string(),
        )

        # Mostramos las estadísticas descriptivas

        logger.info(
            "Estadísticas descriptivas:\n%s",
            dataframe.describe(include="all").to_string(),
        )

        # Comprobamos los valores nulos

        null_values = dataframe.isna().sum()

        total_nulls = null_values.sum()

        logger.info(
            "Valores nulos: %d",
            total_nulls,
        )

        # Comprobamos los registros duplicados

        duplicated_rows = dataframe.duplicated().sum()

        logger.info(
            "Registros duplicados: %d",
            duplicated_rows,
        )

    # Resumen general

    logger.info("RESUMEN GENERAL")

    logger.info("Agencias: %d", len(agency))
    logger.info("Rutas: %d", len(routes))
    logger.info("Viajes: %d", len(trips))
    logger.info("Paradas: %d", len(stops))
    logger.info("Stop Times: %d", len(stop_times))
    logger.info("Calendarios: %d", len(calendar))

    # Tipos de transporte

    logger.info("TIPOS DE TRANSPORTE")

    route_types = routes["route_type"].value_counts()

    for route_type, count in route_types.items():

        logger.info(
            "route_type %s: %d rutas",
            route_type,
            count,
        )

    # Principales rutas

    logger.info("PRINCIPALES RUTAS")

    route_summary = (
        routes[
            [
                "route_short_name",
                "route_long_name",
                "route_type",
            ]
        ]
        .sort_values("route_short_name")
    )

    for _, route in route_summary.head(20).iterrows():

        logger.info(
            "%s - %s",
            route["route_short_name"],
            route["route_long_name"],
        )

    # Calidad de paradas

    logger.info("CALIDAD DE PARADAS")

    missing_coordinates = stops[
        stops["stop_lat"].isna()
        | stops["stop_lon"].isna()
        | (stops["stop_lat"] == "")
        | (stops["stop_lon"] == "")
    ]

    logger.info(
        "Paradas sin coordenadas: %d",
        len(missing_coordinates),
    )

    # Stop ID duplicados

    duplicate_stops = stops["stop_id"].duplicated().sum()

    logger.info(
        "stop_id duplicados: %d",
        duplicate_stops,
    )

    # Relaciones entre tablas

    logger.info("RELACIONES ENTRE TABLAS")

    route_ids = set(routes["route_id"])
    trip_route_ids = set(trips["route_id"])

    missing_routes = trip_route_ids - route_ids

    logger.info(
        "Viajes con route_id inexistente: %d",
        len(missing_routes),
    )

    stop_ids = set(stops["stop_id"])
    stop_time_ids = set(stop_times["stop_id"])

    missing_stops = stop_time_ids - stop_ids

    logger.info(
        "Stop Times con stop_id inexistente: %d",
        len(missing_stops),
    )

    trip_ids = set(trips["trip_id"])
    stop_time_trip_ids = set(stop_times["trip_id"])

    missing_trips = stop_time_trip_ids - trip_ids

    logger.info(
        "Stop Times con trip_id inexistente: %d",
        len(missing_trips),
    )

    # Estadísticas de viajes

    logger.info("ESTADÍSTICAS DE VIAJES")

    trips_per_route = trips.groupby(
        "route_id"
    ).size()

    logger.info(
        "Media de viajes por ruta: %.2f",
        trips_per_route.mean(),
    )

    logger.info(
        "Máximo de viajes en una ruta: %d",
        trips_per_route.max(),
    )

    logger.info(
        "Mínimo de viajes en una ruta: %d",
        trips_per_route.min(),
    )

    # Análisis final de los datos

    logger.info("ANÁLISIS FINAL DE LOS DATOS")

    for filename, dataframe in important_files.items():

        logger.info("%s", filename)

        # Comprobamos los valores nulos finales

        null_values = dataframe.isna().sum()

        total_nulls = null_values.sum()

        logger.info(
            "Valores nulos finales: %d",
            total_nulls,
        )

        # Comprobamos los registros duplicados finales

        duplicated_rows = dataframe.duplicated().sum()

        logger.info(
            "Registros duplicados finales: %d",
            duplicated_rows,
        )

    logger.info("ANÁLISIS DE DATOS COMPLETADO CORRECTAMENTE")


def main():
    try:

        gtfs_path = get_latest_gtfs()

        analyze_gtfs(gtfs_path)

    except (OSError, ValueError, KeyError) as error:

        logger.error(
            "Error durante el análisis del GTFS: %s",
            error,
        )

        raise


if __name__ == "__main__":
    main()