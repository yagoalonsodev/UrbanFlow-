import logging
import os
from pathlib import Path

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("urbanflow")


BASE_DIR = Path("/app")

RAW_BASE_DIR = (
    BASE_DIR
    / "data"
    / "raw"
    / "tmb"
)

PROCESSED_BASE_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "tmb"
)

MINIO_ENDPOINT = "http://minio:9000"

MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")

BUCKET_NAME = "urbanflow"


def create_minio_client():
    """Crea el cliente para conectarse con MinIO."""

    logger.info("Conectando con MinIO...")

    client = boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )

    logger.info(
        "Conexión con MinIO establecida correctamente."
    )

    return client


def validate_bucket(client) -> None:
    """Comprueba que el bucket existe."""

    logger.info(
        "Comprobando bucket: %s",
        BUCKET_NAME,
    )

    try:
        client.head_bucket(
            Bucket=BUCKET_NAME
        )

    except ClientError as error:
        raise RuntimeError(
            f"El bucket '{BUCKET_NAME}' no existe "
            "o no se puede acceder a él."
        ) from error

    logger.info(
        "Bucket '%s' disponible correctamente.",
        BUCKET_NAME,
    )


def get_snapshot_directories(directory: Path):
    """Obtiene únicamente snapshots con formato YYYY-MM-DD."""

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


def get_files(directory: Path):
    """Obtiene únicamente archivos de datos válidos."""

    return [
        file
        for file in directory.rglob("*")
        if file.is_file()
        and file.suffix.lower() in {".csv", ".zip"}
    ]


def upload_snapshot(
    client,
    snapshot_dir: Path,
    prefix: str,
) -> None:
    """Sube un snapshot completo a MinIO."""

    files = get_files(snapshot_dir)

    logger.info(
        "Snapshot %s: %d archivos encontrados.",
        snapshot_dir.name,
        len(files),
    )

    for file in files:

        relative_path = file.relative_to(snapshot_dir)

        object_name = (
            f"{prefix}/{snapshot_dir.name}/{relative_path}"
        )

        client.upload_file(
            str(file),
            BUCKET_NAME,
            object_name,
        )

        logger.info(
            "Subido: %s",
            object_name,
        )


def upload_all_snapshots(
    client,
    base_directory: Path,
    prefix: str,
) -> None:
    """Sube todos los snapshots disponibles."""

    snapshots = get_snapshot_directories(
        base_directory
    )

    if not snapshots:
        raise FileNotFoundError(
            f"No se encontraron snapshots en {base_directory}"
        )

    logger.info(
        "Encontrados %d snapshots en %s",
        len(snapshots),
        base_directory,
    )

    for snapshot in snapshots:

        upload_snapshot(
            client,
            snapshot,
            prefix,
        )


def main():
    logger.info(
        "URBANFLOW - CARGA DE DATOS A MINIO"
    )

    client = create_minio_client()

    validate_bucket(client)

    logger.info(
        "Subiendo snapshots RAW..."
    )

    upload_all_snapshots(
        client,
        RAW_BASE_DIR,
        "raw/tmb",
    )

    logger.info(
        "Snapshots RAW subidos correctamente."
    )

    logger.info(
        "Subiendo snapshots PROCESSED..."
    )

    upload_all_snapshots(
        client,
        PROCESSED_BASE_DIR,
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