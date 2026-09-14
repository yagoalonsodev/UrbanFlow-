import os

from pathlib import Path
from dotenv import load_dotenv


# CARGAR VARIABLES DEL .ENV

BASE_PROJECT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_PROJECT_DIR / ".env")


# PROJECT

BASE_DIR = Path(
    os.getenv("URBANFLOW_BASE_DIR", str(BASE_PROJECT_DIR))
)


# DATA LAKE

TMB_RAW_DIR = (
    BASE_DIR
    / "data"
    / "raw"
    / "tmb"
)

TMB_PROCESSED_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "tmb"
)


# TMB

TMB_APP_ID = os.getenv("TMB_APP_ID")
TMB_APP_KEY = os.getenv("TMB_APP_KEY")


# POSTGRESQL

POSTGRES_DB = os.getenv(
    "POSTGRES_DB",
    "urbanflow",
)

POSTGRES_USER = os.getenv(
    "POSTGRES_USER",
    "urbanflow",
)

POSTGRES_PASSWORD = os.getenv(
    "POSTGRES_PASSWORD",
)

POSTGRES_PORT = os.getenv(
    "POSTGRES_PORT",
    "5432",
)

POSTGRES_HOST = os.getenv(
    "POSTGRES_HOST",
)


# PostgreSQL SQLAlchemy

POSTGRES_DATABASE_URL = (
    "postgresql+psycopg2://"
    f"{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}"
    f"/{POSTGRES_DB}"
)


# PostgreSQL JDBC

POSTGRES_URL = (
    f"jdbc:postgresql://"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}"
    f"/{POSTGRES_DB}"
)


# MINIO

MINIO_ROOT_USER = os.getenv(
    "MINIO_ROOT_USER",
)

MINIO_ROOT_PASSWORD = os.getenv(
    "MINIO_ROOT_PASSWORD",
)
MINIO_ENDPOINT = os.getenv(
    "MINIO_ENDPOINT",
    "localhost:9000",
)

MINIO_BUCKET = os.getenv(
    "MINIO_BUCKET",
    "urbanflow",
)