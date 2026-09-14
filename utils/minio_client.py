from pathlib import Path

from minio import Minio
from minio.error import S3Error

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


def ensure_bucket(client=None) -> None:
    """Crea el bucket configurado si todavía no existe."""

    client = client or create_minio_client()

    try:
        if not client.bucket_exists(MINIO_BUCKET):
            client.make_bucket(MINIO_BUCKET)
    except S3Error as error:
        if error.code != "BucketAlreadyOwnedByYou":
            raise


def upload_file(
    file_path: Path,
    object_name: str,
) -> None:
    """
    Sube un archivo a MinIO.
    """

    client = create_minio_client()
    ensure_bucket(client)

    client.fput_object(
        MINIO_BUCKET,
        object_name,
        str(file_path),
    )

    print(
        f"Archivo subido a MinIO: {object_name}"
    )