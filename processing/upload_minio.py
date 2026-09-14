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
):
    """
    Obtiene únicamente archivos de datos válidos.
    """

    return [
        file
        for file in directory.rglob("*")
        if file.is_file()
        and file.suffix.lower() in {".csv", ".zip"}
    ]


def upload_snapshot(
    snapshot_dir: Path,
    prefix: str,
) -> None:
    """
    Sube un snapshot completo a MinIO.
    """

    files = get_files(
        snapshot_dir
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


def upload_all_snapshots(
    base_directory: Path,
    prefix: str,
) -> None:
    """
    Sube todos los snapshots disponibles.
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
        "Encontrados %d snapshots en %s",
        len(snapshots),
        base_directory,
    )

    for snapshot in snapshots:

        upload_snapshot(
            snapshot,
            prefix,
        )


def main():
    logger.info(
        "URBANFLOW - CARGA DE DATOS A MINIO"
    )

    logger.info(
        "Subiendo snapshots RAW..."
    )

    upload_all_snapshots(
        TMB_RAW_DIR,
        "raw/tmb",
    )

    logger.info(
        "Snapshots RAW subidos correctamente."
    )

    logger.info(
        "Subiendo snapshots PROCESSED..."
    )

    upload_all_snapshots(
        TMB_PROCESSED_DIR,
        "processed/tmb",
    )

    logger.info(
        "Snapshots PROCESSED subidos correctamente."
    )

    logger.info(
        "CARGA A MINIO COMPLETADA CORRECTAMENTE"
    )


if __name__ == "__main__":
    main()