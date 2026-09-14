from pathlib import Path

from minio import Minio

from utils.config import (
    MINIO_BUCKET,
    MINIO_ENDPOINT,
    MINIO_ROOT_PASSWORD,
    MINIO_ROOT_USER,
)


def create_minio_client():
    """
    Crea el cliente de MinIO.
    """

    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ROOT_USER,
        secret_key=MINIO_ROOT_PASSWORD,
        secure=False,
    )


def upload_file(
    file_path: Path,
    object_name: str,
) -> None:
    """
    Sube un archivo a MinIO.
    """

    client = create_minio_client()

    client.fput_object(
        MINIO_BUCKET,
        object_name,
        str(file_path),
    )

    print(
        f"Archivo subido a MinIO: {object_name}"
    )