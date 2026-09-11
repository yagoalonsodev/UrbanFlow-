import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

from utils.config import (
    POSTGRES_DATABASE_URL,
    TMB_PROCESSED_DIR,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("urbanflow")


PROCESSED_BASE_DIR = TMB_PROCESSED_DIR


DATASETS = [
    "agency",
    "routes",
    "stops",
    "calendar",
    "calendar_dates",
    "trips",
    "stop_times",
]

DELETE_ORDER = [
    "stop_times",
    "trips",
    "calendar_dates",
    "calendar",
    "stops",
    "routes",
    "agency",
]

def get_latest_processed_snapshot() -> Path:
    """Obtiene el snapshot Processed más reciente."""

    snapshot_dirs = [
        directory
        for directory in PROCESSED_BASE_DIR.iterdir()
        if directory.is_dir()
        and len(directory.name) == 10
        and directory.name[4] == "-"
        and directory.name[7] == "-"
    ]

    if not snapshot_dirs:
        raise FileNotFoundError(
            "No se encontraron snapshots procesados."
        )

    latest_snapshot = max(
        snapshot_dirs,
        key=lambda directory: directory.name,
    )

    logger.info(
        "Snapshot Processed seleccionado: %s",
        latest_snapshot.name,
    )

    return latest_snapshot


def create_database_engine():
    """Crea la conexión con PostgreSQL."""

    logger.info("Conectando con PostgreSQL...")

    engine = create_engine(POSTGRES_DATABASE_URL)

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    logger.info(
        "Conexión con PostgreSQL establecida correctamente."
    )

    return engine


def delete_snapshot(
    engine,
    snapshot_date,
) -> None:
    """
    Elimina únicamente el snapshot que se va a cargar.

    Esto permite volver a ejecutar el DAG el mismo día
    sin generar registros duplicados.
    """

    logger.info(
        "Eliminando snapshot existente: %s",
        snapshot_date,
    )

    with engine.begin() as connection:

        for dataset in DELETE_ORDER:

            connection.execute(
                text(
                    f"""
                    DELETE FROM {dataset}
                    WHERE snapshot_date = :snapshot_date
                    """
                ),
                {
                    "snapshot_date": snapshot_date,
                },
            )

    logger.info(
        "Snapshot %s eliminado correctamente.",
        snapshot_date,
    )


def load_dataset(
    engine,
    dataset_name: str,
    processed_snapshot: Path,
    snapshot_date,
) -> None:
    """Carga un dataset Processed en PostgreSQL."""

    dataset_dir = processed_snapshot / dataset_name

    csv_files = [
        file
        for file in dataset_dir.glob("*.csv")
        if not file.name.startswith("_")
    ]

    if not csv_files:
        raise FileNotFoundError(
            f"No se encontraron CSV para {dataset_name}: "
            f"{dataset_dir}"
        )

    logger.info(
        "Cargando dataset: %s",
        dataset_name,
    )

    dataframes = [
        pd.read_csv(file)
        for file in csv_files
    ]

    dataframe = pd.concat(
        dataframes,
        ignore_index=True,
    )

    # Añadimos la fecha del snapshot.
    dataframe["snapshot_date"] = snapshot_date

    dataframe.to_sql(
        dataset_name,
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000,
    )

    logger.info(
        "%s cargado correctamente: %d registros "
        "(snapshot: %s)",
        dataset_name,
        len(dataframe),
        snapshot_date,
    )


def validate_counts(
    engine,
    snapshot_date,
) -> None:
    """Comprueba el número de registros del snapshot cargado."""

    logger.info(
        "VALIDACIÓN DE REGISTROS - SNAPSHOT %s",
        snapshot_date,
    )

    with engine.connect() as connection:

        for dataset in DATASETS:

            result = connection.execute(
                text(
                    f"""
                    SELECT COUNT(*)
                    FROM {dataset}
                    WHERE snapshot_date = :snapshot_date
                    """
                ),
                {
                    "snapshot_date": snapshot_date,
                },
            )

            count = result.scalar()

            logger.info(
                "%s: %d registros",
                dataset,
                count,
            )


def validate_history(
    engine,
) -> None:
    """Muestra los snapshots almacenados históricamente."""

    logger.info("HISTÓRICO DE SNAPSHOTS")

    with engine.connect() as connection:

        result = connection.execute(
            text(
                """
                SELECT
                    snapshot_date,
                    COUNT(*) AS total_registros
                FROM trips
                GROUP BY snapshot_date
                ORDER BY snapshot_date
                """
            )
        )

        rows = result.fetchall()

        if not rows:
            logger.info(
                "No existen snapshots históricos."
            )
            return

        for row in rows:

            logger.info(
                "Snapshot %s: %d viajes",
                row.snapshot_date,
                row.total_registros,
            )


def main():

    logger.info(
        "URBANFLOW - CARGA POSTGRESQL HISTÓRICA"
    )

    processed_snapshot = get_latest_processed_snapshot()

    # El nombre del directorio es YYYY-MM-DD.
    snapshot_date = pd.to_datetime(
        processed_snapshot.name,
        format="%Y-%m-%d",
    ).date()

    logger.info(
        "Fecha del snapshot: %s",
        snapshot_date,
    )

    engine = create_database_engine()

    # Eliminamos solamente ese día.
    # Los snapshots anteriores permanecen intactos.
    delete_snapshot(
        engine,
        snapshot_date,
    )

    for dataset in DATASETS:

        load_dataset(
            engine,
            dataset,
            processed_snapshot,
            snapshot_date,
        )

    validate_counts(
        engine,
        snapshot_date,
    )

    validate_history(
        engine,
    )

    logger.info(
        "CARGA POSTGRESQL HISTÓRICA "
        "COMPLETADA CORRECTAMENTE"
    )


if __name__ == "__main__":
    main()