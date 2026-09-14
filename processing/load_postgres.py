import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from utils.config import POSTGRES_DATABASE_URL, TMB_PROCESSED_DIR


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

    year_dirs = [
        directory
        for directory in TMB_PROCESSED_DIR.iterdir()
        if directory.is_dir()
        and directory.name.startswith("year=")
    ]

    if not year_dirs:
        raise FileNotFoundError(
            "No se encontraron snapshots procesados."
        )

    latest_year = max(
        year_dirs,
        key=lambda directory: directory.name,
    )

    month_dirs = [
        directory
        for directory in latest_year.iterdir()
        if directory.is_dir()
        and directory.name.startswith("month=")
    ]

    if not month_dirs:
        raise FileNotFoundError(
            f"No se encontraron meses en {latest_year}"
        )

    latest_month = max(
        month_dirs,
        key=lambda directory: directory.name,
    )

    day_dirs = [
        directory
        for directory in latest_month.iterdir()
        if directory.is_dir()
        and directory.name.startswith("day=")
    ]

    if not day_dirs:
        raise FileNotFoundError(
            f"No se encontraron días en {latest_month}"
        )

    latest_day = max(
        day_dirs,
        key=lambda directory: directory.name,
    )

    logger.info(
        "Snapshot Processed seleccionado: %s/%s/%s",
        latest_year.name,
        latest_month.name,
        latest_day.name,
    )

    return latest_day


def get_snapshot_date(snapshot_dir: Path):
    """Obtiene la fecha del snapshot a partir de sus carpetas."""

    year = snapshot_dir.parent.parent.name.replace(
        "year=",
        "",
    )

    month = snapshot_dir.parent.name.replace(
        "month=",
        "",
    )

    day = snapshot_dir.name.replace(
        "day=",
        "",
    )

    return pd.to_datetime(
        f"{year}-{month}-{day}",
        format="%Y-%m-%d",
    ).date()


def create_database_engine() -> Engine:
    """Crea la conexión con PostgreSQL."""

    logger.info("Conectando con PostgreSQL...")

    engine = create_engine(
        POSTGRES_DATABASE_URL
    )

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    logger.info(
        "Conexión con PostgreSQL establecida correctamente."
    )

    return engine


def delete_snapshot(
    engine: Engine,
    snapshot_date,
) -> None:
    """Elimina únicamente el snapshot que se va a cargar."""

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
    engine: Engine,
    dataset_name: str,
    processed_snapshot: Path,
    snapshot_date,
) -> None:
    """Carga un dataset Processed en PostgreSQL."""

    dataset_dir = (
        processed_snapshot
        / dataset_name
    )

    parquet_files = [
        file
        for file in dataset_dir.glob("*.parquet")
        if not file.name.startswith("_")
    ]

    if not parquet_files:
        raise FileNotFoundError(
            f"No se encontraron archivos Parquet para "
            f"{dataset_name}: {dataset_dir}"
        )

    logger.info(
        "Cargando dataset: %s",
        dataset_name,
    )

    dataframes = [
        pd.read_parquet(file)
        for file in parquet_files
    ]

    dataframe = pd.concat(
        dataframes,
        ignore_index=True,
    )

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
    engine: Engine,
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
    engine: Engine,
) -> None:
    """Muestra los snapshots almacenados históricamente."""

    logger.info(
        "HISTÓRICO DE SNAPSHOTS"
    )

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

    processed_snapshot = (
        get_latest_processed_snapshot()
    )

    snapshot_date = get_snapshot_date(
        processed_snapshot
    )

    logger.info(
        "Fecha del snapshot: %s",
        snapshot_date,
    )

    engine = create_database_engine()

    try:
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
            engine
        )

        logger.info(
            "CARGA POSTGRESQL HISTÓRICA "
            "COMPLETADA CORRECTAMENTE"
        )

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()