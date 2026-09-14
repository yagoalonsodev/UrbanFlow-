import logging

from datetime import datetime
from pathlib import Path
from zipfile import ZipFile, BadZipFile

import requests

from utils.config import (
    TMB_APP_ID,
    TMB_APP_KEY,
    TMB_RAW_DIR,
)

from utils.constants import (
    TMB_BASE_URL,
)


# Validación de configuración TMB

if not TMB_APP_ID:
    raise ValueError("La variable TMB_APP_ID no está configurada.")

if not TMB_APP_KEY:
    raise ValueError("La variable TMB_APP_KEY no está configurada.")


TMB_RAW_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


logger = logging.getLogger(__name__)


def download_gtfs() -> Path:
    """
    Sacamos el GTFS diario y lo guardamos en Data Lake Raw.
    """

    date = datetime.now().strftime("%Y-%m-%d")

    output_dir = TMB_RAW_DIR / date
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = output_dir / "tmb_gtfs.zip"

    logger.info(
        "Iniciando descarga del GTFS de TMB..."
    )

    logger.info(
        "URL: %s",
        TMB_BASE_URL,
    )

    response = requests.get(
        TMB_BASE_URL,
        params={
            "app_id": TMB_APP_ID,
            "app_key": TMB_APP_KEY,
        },
        timeout=60,
    )

    response.raise_for_status()

    output_file.write_bytes(
        response.content
    )

    logger.info(
        "GTFS descargado correctamente: %s",
        output_file,
    )

    logger.info(
        "Tamaño del archivo: %.2f MB",
        output_file.stat().st_size / (1024 * 1024),
    )

    return output_file


def validate_gtfs(gtfs_path: Path) -> None:

    """
    Comprobamos que el archivo es un zip con
    GTFS obligatorios.
    """

    logger.info(
        "Validando archivo GTFS..."
    )

    required_files = {
        "agency.txt",
        "stops.txt",
        "routes.txt",
        "trips.txt",
        "stop_times.txt",
        "calendar.txt",
    }

    try:
        with ZipFile(
            gtfs_path,
            "r",
        ) as zip_file:

            files = {
                Path(file).name
                for file in zip_file.namelist()
            }

    except BadZipFile as error:
        raise ValueError(
            "El archivo descargado no es un ZIP válido."
        ) from error

    missing_files = required_files - files

    if missing_files:
        raise ValueError(
            f"Faltan archivos GTFS obligatorios: {missing_files}"
        )

    logger.info(
        "Validación GTFS completada correctamente."
    )

    logger.info(
        "Archivos encontrados: %d",
        len(files),
    )


def extract_gtfs(gtfs_path: Path) -> Path:
    """
    Extraemos el ZIP GTFS en la carpeta extracted.
    """

    extracted_dir = (
        gtfs_path.parent / "extracted"
    )

    extracted_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger.info(
        "Extrayendo archivo GTFS..."
    )

    try:
        with ZipFile(
            gtfs_path,
            "r",
        ) as zip_file:

            zip_file.extractall(
                extracted_dir
            )

    except BadZipFile as error:
        raise ValueError(
            "No se puede extraer el archivo porque no es un ZIP válido."
        ) from error

    logger.info(
        "GTFS extraído correctamente: %s",
        extracted_dir,
    )

    return extracted_dir


def main():
    logger.info(
        "URBANFLOW BARCELONA - TMB GTFS INGESTION"
    )

    try:
        gtfs_path = download_gtfs()

        validate_gtfs(
            gtfs_path
        )

        extract_gtfs(
            gtfs_path
        )

        logger.info(
            "INGESTA COMPLETADA CORRECTAMENTE"
        )

    except requests.RequestException as error:
        logger.error(
            "Error descargando el GTFS: %s",
            error,
        )
        raise

    except (OSError, ValueError) as error:
        logger.error(
            "Error procesando el GTFS: %s",
            error,
        )
        raise


if __name__ == "__main__":
    main()