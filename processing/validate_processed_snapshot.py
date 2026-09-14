import logging
from pathlib import Path

import pandas as pd

from processing.load_postgres import get_latest_processed_snapshot, get_snapshot_date


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("urbanflow")


DATASETS = [
    "agency",
    "routes",
    "stops",
    "calendar",
    "calendar_dates",
    "trips",
    "stop_times",
]


REQUIRED_COLUMNS = {
    "agency": {"agency_name"},
    "routes": {"route_id"},
    "stops": {"stop_id"},
    "calendar": {"service_id"},
    "calendar_dates": {"service_id", "date"},
    "trips": {"trip_id", "route_id", "service_id"},
    "stop_times": {"trip_id", "stop_id", "stop_sequence"},
}


UNIQUE_COLUMNS = {
    "agency": ["agency_name"],
    "routes": ["route_id"],
    "stops": ["stop_id"],
    "calendar": ["service_id"],
    "calendar_dates": ["service_id", "date"],
    "trips": ["trip_id"],
    "stop_times": ["trip_id", "stop_id", "stop_sequence"],
}


IDENTIFIER_COLUMNS = {
    "agency": ["agency_name"],
    "routes": ["route_id"],
    "stops": ["stop_id"],
    "calendar": ["service_id"],
    "calendar_dates": ["service_id"],
    "trips": ["trip_id", "route_id", "service_id"],
    "stop_times": ["trip_id", "stop_id"],
}


def load_processed_dataframes(snapshot_dir: Path) -> dict[str, pd.DataFrame]:
    dataframes = {}

    for dataset in DATASETS:
        dataset_dir = snapshot_dir / dataset
        parquet_files = sorted(dataset_dir.glob("*.parquet"))

        if not parquet_files:
            raise FileNotFoundError(
                f"No se encontraron Parquet para {dataset}: {dataset_dir}"
            )

        dataframe = pd.concat(
            [pd.read_parquet(file) for file in parquet_files],
            ignore_index=True,
        )

        if dataframe.empty:
            raise ValueError(f"El dataset procesado {dataset} no contiene registros.")

        dataframes[dataset] = dataframe

    return dataframes


def validate_processed_dataframes(
    dataframes: dict[str, pd.DataFrame],
) -> dict[str, int]:
    for dataset in DATASETS:
        if dataset not in dataframes:
            raise ValueError(f"Falta el dataset procesado {dataset}.")

        dataframe = dataframes[dataset]
        missing_columns = REQUIRED_COLUMNS[dataset] - set(dataframe.columns)
        if missing_columns:
            raise ValueError(
                f"{dataset} no contiene las columnas obligatorias: {missing_columns}"
            )

        null_identifiers = dataframe[IDENTIFIER_COLUMNS[dataset]].isnull().sum()
        invalid_nulls = null_identifiers[null_identifiers > 0]
        if not invalid_nulls.empty:
            raise ValueError(
                f"{dataset} contiene identificadores nulos: {invalid_nulls.to_dict()}"
            )

        duplicate_count = dataframe.duplicated(
            subset=UNIQUE_COLUMNS[dataset]
        ).sum()
        if duplicate_count:
            raise ValueError(
                f"{dataset} contiene {duplicate_count} claves duplicadas."
            )

    routes = set(dataframes["routes"]["route_id"])
    invalid_routes = set(dataframes["trips"]["route_id"]) - routes
    if invalid_routes:
        raise ValueError(
            f"trips contiene route_id sin correspondencia: {sorted(invalid_routes)[:5]}"
        )

    trips = set(dataframes["trips"]["trip_id"])
    invalid_trips = set(dataframes["stop_times"]["trip_id"]) - trips
    if invalid_trips:
        raise ValueError(
            f"stop_times contiene trip_id sin correspondencia: {sorted(invalid_trips)[:5]}"
        )

    stops = set(dataframes["stops"]["stop_id"])
    invalid_stops = set(dataframes["stop_times"]["stop_id"]) - stops
    if invalid_stops:
        raise ValueError(
            f"stop_times contiene stop_id sin correspondencia: {sorted(invalid_stops)[:5]}"
        )

    counts = {dataset: len(dataframes[dataset]) for dataset in DATASETS}
    for dataset, count in counts.items():
        logger.info("%s: %d registros procesados", dataset, count)

    return counts


def validate_processed_snapshot(snapshot_dir: Path) -> dict[str, int]:
    logger.info("Validando snapshot procesado: %s", snapshot_dir)
    return validate_processed_dataframes(load_processed_dataframes(snapshot_dir))


def main() -> None:
    snapshot_dir = get_latest_processed_snapshot()
    snapshot_date = get_snapshot_date(snapshot_dir)
    logger.info("Snapshot procesado seleccionado: %s", snapshot_date)
    validate_processed_snapshot(snapshot_dir)
    logger.info("VALIDACIÓN DEL SNAPSHOT PROCESADO COMPLETADA CORRECTAMENTE")


if __name__ == "__main__":
    main()