import os
from pathlib import Path

import pytest

import utils.minio_client as minio_client


class FakeMinioClient:
    def __init__(self, bucket_exists=False):
        self._bucket_exists = bucket_exists
        self.created_buckets = []
        self.uploads = []

    def bucket_exists(self, bucket):
        return self._bucket_exists

    def make_bucket(self, bucket):
        self.created_buckets.append(bucket)
        self._bucket_exists = True

    def fput_object(self, bucket, object_name, file_path):
        self.uploads.append((bucket, object_name, file_path))


def test_ensure_bucket_creates_missing_bucket(monkeypatch):
    client = FakeMinioClient()

    minio_client.ensure_bucket(client)

    assert client.created_buckets == [minio_client.MINIO_BUCKET]


def test_ensure_bucket_does_not_recreate_existing_bucket():
    client = FakeMinioClient(bucket_exists=True)

    minio_client.ensure_bucket(client)

    assert client.created_buckets == []


def test_upload_file_ensures_bucket_and_uploads(monkeypatch, tmp_path):
    client = FakeMinioClient()
    file_path = tmp_path / "example.txt"
    file_path.write_text("urbanflow")

    monkeypatch.setattr(minio_client, "create_minio_client", lambda: client)

    minio_client.upload_file(file_path, "raw/example.txt")

    assert client.created_buckets == [minio_client.MINIO_BUCKET]
    assert client.uploads == [
        (minio_client.MINIO_BUCKET, "raw/example.txt", str(file_path))
    ]


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("MINIO_INTEGRATION") != "1",
    reason="Requiere MINIO_INTEGRATION=1 y conectividad con MinIO.",
)
def test_real_minio_bucket_and_upload():
    """Comprueba MinIO real cuando se ejecuta la suite dentro de Docker."""

    client = minio_client.create_minio_client()
    minio_client.ensure_bucket(client)

    test_file = Path("/tmp/urbanflow-minio-test.txt")
    test_file.write_text("urbanflow-minio-integration")
    object_name = "tests/urbanflow-minio-test.txt"

    minio_client.upload_file(test_file, object_name)

    response = client.get_object(minio_client.MINIO_BUCKET, object_name)
    try:
        assert response.read() == b"urbanflow-minio-integration"
    finally:
        response.close()
        response.release_conn()
        client.remove_object(minio_client.MINIO_BUCKET, object_name)