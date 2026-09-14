import logging

from pathlib import Path

from utils.config import (
    TMB_PROCESSED_DIR,
    TMB_RAW_DIR,
)

from utils.minio_client import (
    upload_file,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("urbanflow")


def get_snapshot_directories(
    directory: Path,
):
    """
    Obtiene únicamente snapshots con formato YYYY-MM-DD.
    """

    if not directory.exists():
        raise FileNotFoundError(
            f"No existe el directorio: {directory}"
        )

    return sorted(
        [
            snapshot
            for snapshot in directory.iterdir()
            if snapshot.is_dir()
            and len(snapshot.name) == 10
            and snapshot.name[4] == "-"
            and snapshot.name[7] == "-"
        ],
        key=lambda snapshot: snapshot.name,
    )


def get_files(
    directory: Path,
    extensions: set[str],
):
    """
    Obtiene únicamente archivos con las extensiones indicadas.
    """

    return [
        file
        for file in directory.rglob("*")
        if file.is_file()
        and file.suffix.lower() in extensions
    ]


def upload_snapshot(
    snapshot_dir: Path,
    prefix: str,
) -> None:
    """
    Sube un snapshot RAW completo a MinIO.
    """

    files = get_files(
        snapshot_dir,
        {".zip"},
    )

    logger.info(
        "Snapshot %s: %d archivos encontrados.",
        snapshot_dir.name,
        len(files),
    )

    for file in files:

        relative_path = file.relative_to(
            snapshot_dir
        )

        object_name = (
            f"{prefix}/"
            f"year={snapshot_dir.name[:4]}/"
            f"month={snapshot_dir.name[5:7]}/"
            f"day={snapshot_dir.name[8:10]}/"
            f"{relative_path}"
        )

        upload_file(
            file,
            object_name,
        )


def upload_all_raw_snapshots(
    base_directory: Path,
    prefix: str,
) -> None:
    """
    Sube todos los snapshots RAW disponibles.
    """

    snapshots = get_snapshot_directories(
        base_directory
    )

    if not snapshots:
        raise FileNotFoundError(
            f"No se encontraron snapshots en "
            f"{base_directory}"
        )

    logger.info(
        "Encontrados %d snapshots RAW en %s",
        len(snapshots),
        base_directory,
    )

    for snapshot in snapshots:

        upload_snapshot(
            snapshot,
            prefix,
        )


def upload_processed(
    base_directory: Path,
    prefix: str,
) -> None:
    """
    Sube los datos PROCESSED en formato Parquet.
    """

    files = get_files(
        base_directory,
        {".parquet"},
    )

    if not files:
        raise FileNotFoundError(
            f"No se encontraron archivos Parquet en "
            f"{base_directory}"
        )

    logger.info(
        "Encontrados %d archivos Parquet PROCESSED.",
        len(files),
    )

    for file in files:

        relative_path = file.relative_to(
            base_directory
        )

        object_name = (
            f"{prefix}/"
            f"{relative_path}"
        )

        upload_file(
            file,
            object_name,
        )


def main():
    logger.info(
        "URBANFLOW - CARGA DE DATOS A MINIO"
    )

    logger.info(
        "Subiendo snapshots RAW..."
    )

    upload_all_raw_snapshots(
        TMB_RAW_DIR,
        "raw/tmb",
    )

    logger.info(
        "Snapshots RAW subidos correctamente."
    )

    logger.info(
        "Subiendo datos PROCESSED en Parquet..."
    )

    upload_processed(
        TMB_PROCESSED_DIR,
        "processed/tmb",
    )

    logger.info(
        "Datos PROCESSED subidos correctamente."
    )

    logger.info(
        "CARGA A MINIO COMPLETADA CORRECTAMENTE"
    )


if __name__ == "__main__":
    main()