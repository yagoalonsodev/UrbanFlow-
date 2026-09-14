from pathlib import Path
from zipfile import ZipFile

import pytest


REQUIRED_FILES = {
    "agency.txt",
    "stops.txt",
    "routes.txt",
    "trips.txt",
    "stop_times.txt",
    "calendar.txt",
}


@pytest.fixture
def download_module(monkeypatch, tmp_path):
    """
    Importa download_gtfs con credenciales ficticias
    y una carpeta temporal para los datos Raw.
    """

    monkeypatch.setenv("TMB_APP_ID", "test-app-id")
    monkeypatch.setenv("TMB_APP_KEY", "test-app-key")

    import sys
    import utils.config

    monkeypatch.setattr(
        utils.config,
        "TMB_APP_ID",
        "test-app-id",
    )
    monkeypatch.setattr(
        utils.config,
        "TMB_APP_KEY",
        "test-app-key",
    )

    monkeypatch.setattr(
        utils.config,
        "TMB_RAW_DIR",
        tmp_path / "raw",
    )

    sys.modules.pop("ingestion.download_gtfs", None)

    import ingestion.download_gtfs as download_gtfs

    return download_gtfs

def create_gtfs_zip(
    zip_path: Path,
    files: set[str],
) -> None:
    """Crea un ZIP GTFS de prueba."""

    with ZipFile(zip_path, "w") as zip_file:
        for file_name in files:
            zip_file.writestr(
                file_name,
                "test,data\n1,example\n",
            )


def test_validate_gtfs_accepts_valid_zip(
    tmp_path,
    download_module,
):
    """Un ZIP con todos los archivos obligatorios debe ser válido."""

    zip_path = tmp_path / "gtfs.zip"

    create_gtfs_zip(
        zip_path,
        REQUIRED_FILES,
    )

    download_module.validate_gtfs(zip_path)


def test_validate_gtfs_rejects_invalid_zip(
    tmp_path,
    download_module,
):
    """Un archivo que no sea ZIP debe provocar un ValueError."""

    zip_path = tmp_path / "invalid.zip"

    zip_path.write_text("esto no es un zip")

    with pytest.raises(ValueError, match="ZIP válido"):
        download_module.validate_gtfs(zip_path)


def test_validate_gtfs_rejects_missing_files(
    tmp_path,
    download_module,
):
    """Un ZIP sin archivos GTFS obligatorios debe fallar."""

    zip_path = tmp_path / "gtfs_incomplete.zip"

    files = REQUIRED_FILES - {"calendar.txt"}

    create_gtfs_zip(
        zip_path,
        files,
    )

    with pytest.raises(
        ValueError,       match="Faltan archivos GTFS obligatorios",
    ):
        download_module.validate_gtfs(zip_path)


def test_extract_gtfs_creates_directory(
    tmp_path,
    download_module,
):
    """La extracción debe crear la carpeta extracted."""

    zip_path = tmp_path / "gtfs.zip"

    create_gtfs_zip(
        zip_path,
        REQUIRED_FILES,
    )

    extracted_dir = download_module.extract_gtfs(zip_path)

    assert extracted_dir.exists()
    assert extracted_dir.is_dir()


def test_extract_gtfs_extracts_required_files(
    tmp_path,
    download_module,
):
    """La extracción debe generar los archivos GTFS."""

    zip_path = tmp_path / "gtfs.zip"

    create_gtfs_zip(
        zip_path,
        REQUIRED_FILES,
    )

    extracted_dir = download_module.extract_gtfs(zip_path)

    for file_name in REQUIRED_FILES:
        assert (extracted_dir / file_name).exists()


def test_download_gtfs_success(
    tmp_path,
    download_module,
    monkeypatch,
):
    """Una descarga correcta debe guardar el ZIP eRaw."""

    class MockResponse:
        content = b"contenido gtfs"

        def raise_for_status(self):
            pass

    def mock_get(url, params, timeout):
        assert url == download_module.TMB_BASE_URL
        assert params == {
            "app_id": "test-app-id",
            "app_key": "test-app-key",
        }
        assert timeout == 60

        return MockResponse()

    monkeypatch.setattr(
        download_module.requests,
        "get",
        mock_get,
    )

    result = download_module.download_gtfs()

    assert result.exists()
    assert result.name == "tmb_gtfs.zip"
    assert result.read_bytes() == b"contenido gtfs"


def test_download_gtfs_http_error(
    download_module,
    monkeypatch,
):
    """Un error HTTP debe propagarse como RequestException."""

    class MockResponse:
        content = b""

        def raise_for_status(self):
            raise download_module.requests.HTTPError(
                "Error HTTP de prueba"
            )

    def mock_get(url, params, timeout):
        return MockResponse()

    monkeypatch.setattr(
        download_module.requests,
        "get",
        mock_get,
    )

    with pytest.raises(
        download_module.requests.HTTPError,
    ):
        download_module.download_gtfs()


def test_download_gtfs_connection_error(
    download_module,
    monkeypatch,
):
    """Un error de conexión debe propagarse."""

    def mock_get(url, params, timeout):
        raise download_module.requests.ConnectionError(
            "Error de conexión de prueba"
        )

    monkeypatch.setattr(
        download_module.requests,
        "get",
        mock_get,
    )

    with pytest.raises(
        download_module.requests.ConnectionError,
    ):
        download_module.download_gtfs()


def test_extract_gtfs_rejects_invalid_zip(
    tmp_path,
    download_module,
):
    """Un ZIP corrupto debe provocar un ValueError."""

    zip_path = tmp_path / "invalid.zip"

    zip_path.write_text("esto no es un ZIP válido")

    with pytest.raises(
        ValueError,
        match="no es un ZIP válido",
    ):
        download_module.extract_gtfs(zip_path)


def test_download_gtfs_creates_date_directory(
    tmp_path,
    download_module,
    monkeypatch,
):
    """La descarga debe guardarse dentro de una carpeta con la fecha actual."""

    class MockResponse:
        content = b"gtfs-test-content"

        def raise_for_status(self):
            pass

    def mock_get(url, params, timeout):
        return MockResponse()

    monkeypatch.setattr(
        download_module.requests,
        "get",
        mock_get,
    )

    result = download_module.download_gtfs()

    assert result.parent.name == download_module.datetime.now().strftime(
        "%Y-%m-%d"
    )
    assert result.name == "tmb_gtfs.zip"
    assert result.parent.parent == tmp_path / "raw"


def test_validate_gtfs_accepts_extra_files(
    tmp_path,
    download_module,
):
    """Un GTFS válido puede contener archivos adicionales."""

    zip_path = tmp_path / "gtfs_extra.zip"

    files = REQUIRED_FILES | {
        "calendar_dates.txt",
        "hapes.txt",
        "frequencies.txt",
    }

    create_gtfs_zip(
        zip_path,
        files,
    )

    download_module.validate_gtfs(zip_path)


def test_validate_gtfs_accepts_nested_files(
    tmp_path,
    download_module,
):
    """Los archivos GTFS deben detectarse aunque estén dentro de una carpeta."""

    zip_path = tmp_path / "gtfs_nested.zip"

    with ZipFile(zip_path, "w") as zip_file:
        for file_name in REQUIRED_FILES:
            zip_file.writestr(
                f"gtfs/{file_name}",
                "test,data\n1,example\n",
            )

    download_module.validate_gtfs(zip_path)


def test_extract_gtfs_preserves_extra_files(
    tmp_path,
    download_module,
):
    """La extracción debe conservar también archivos GTFS adicionales."""

    zip_path = tmp_path / "gtfs_extra.zip"

    files = REQUIRED_FILES | {"shapes.txt"}

    create_gtfs_zip(
        zip_path,
        files,
    )

    extracted_dir = download_module.extract_gtfs(zip_path)

    for file_name in files:
     assert (extracted_dir / file_name).exists()


def test_extract_gtfs_creates_extracted_directory_inside_zip_directory(
    tmp_path,
    download_module,
):
    """La carpeta extracted debe crearse junto al ZIP."""

    zip_directory = tmp_path / "source"
    zip_directory.mkdir()

    zip_path = zip_directory / "tmb_gtfs.zip"

    create_gtfs_zip(
        zip_path,
        REQUIRED_FILES,
    )

    extracted_dir = download_module.extract_gtfs(zip_path)

    assert extracted_dir == zip_directory / "extracted"
    assert extracted_dir.exists()


def test_main_success(
    tmp_path,
    download_module,
    monkeypatch,
):
    """main debe ejecutar correctamente todo el flujo de ingesta."""

    calls = []

    def mock_download():
        calls.append("download")
        return tmp_path / "tmb_gtfs.zip"

    def mock_validate(path):
        calls.append(("validate", path))

    def mock_extract(path):
        calls.append(("extract", path))
        return tmp_path / "extracted"

    monkeypatch.setattr(
        download_module,
        "download_gtfs",
        mock_download,
    )

    monkeypatch.setattr(
        download_module,
        "validate_gtfs",
        mock_validate,
    )

    monkeypatch.setattr(
        download_module,
        "extract_gtfs",
        mock_extract,
    )

    download_module.main()

    assert calls == [
        "download",
        ("validate", tmp_path / "tmb_gtfs.zip"),
        ("extract", tmp_path / "tmb_gtfs.zip"),
    ]


def test_main_propagates_download_error(
    download_module,
    monkeypatch,
):
    """main debe propagar los errores de descarga."""

    error = download_module.requests.ConnectionError(
        "Error de conexión"
    )

    def mock_download():
        raise error

    monkeypatch.setattr(
        download_module,
        "download_gtfs",
        mock_download,
    )

    with pytest.raises(
        download_module.requests.ConnectionError,
        match="Error de conexión",
    ):
        download_module.main()


def test_main_propagates_validati_error(
    tmp_path,
    download_module,
    monkeypatch,
):
    """main debe propagar los errores de validación."""

    zip_path = tmp_path / "tmb_gtfs.zip"

    def mock_download():
        return zip_path

    def mock_validate(path):
        raise ValueError(
            "Faltan archivos GTFS obligatorios"
        )

    monkeypatch.setattr(
        download_module,
        "download_gtfs",
        mock_download,
    )

    monkeypatch.setattr(
        download_module,
        "validate_gtfs",
        mock_validate,
    )

    with pytest.raises(
        ValueError,
        match="Faltan archivos GTFS obligatorios",
    ):
        download_module.main()
def test_download_gtfs_uses_expected_timeout(
    download_module,
    monkeypatch,
):
    """La descarga debe utilizar el timeout configurado de 60 segundos."""

    class MockResponse:
        content = b"gtfs-test-content"

        def raise_for_status(self):
            pass

    captured = {}

    def mock_get(url, params, timeout):
        captured["url"] = url
        captured["params"] = params
        captured["timeout"] = timeout
        return MockResponse()

    monkeypatch.setattr(
        download_module.requests,
        "get",
        mock_get,
    )

    download_module.download_gtfs()

    assert captured["timeout"] == 60


def test_download_gtfs_sends_tmb_credentials(
    download_module,
    monkeypatch,
):
    """La descarga debe enviar las credenciales de TMB."""

    class MockResponse:
        content = b"gtfs-test-content"

        def raise_for_status(self):
            pass

    captured = {}

    def mock_get(url, params, timeout):
        captured["params"] = params
        return MockResponse()

    monkeypatch.setattr(
        download_module.requests,
        "get",
        mock_get,
    )

    download_module.download_gtfs()

    assert captured["params"]["app_id"] == "test-app-id"
    assert captured["params"]["app_key"] == "test-app-key"


def test_download_gtfs_saves_response_content(
    download_module,
    monkeypatch,
):
    """El contenido recibido debe guardarse exactamente en el ZIP."""

    expected_content = b"contenido-gtfs-de-prueba"

    class MockResponse:
        content = expected_content

        def raise_for_status(self):
            pass

    monkeypatch.setattr(
        download_module.requests,
        "get",
        lambda url, params, timeout: MockResponse(),
    )

    result = download_module.download_gtfs()

    assert result.read_bytes() == expected_content


def test_download_gtfs_propagates_os_error(
    download_module,
    monkeypatch,
):
    """Un error de escritura debe propagarse correctamente."""

    class MockResponse:
        content = b"gtfs-test-content"

        def raise_for_status(self):
            pass

    monkeypatch.setattr(
        download_module.requests,
        "get",
        lambda url, params, timeout: MockResponse(),
    )

    def raise_os_error(*args, **kwargs):
        raise OSError("Error de escritura")

    monkeypatch.setattr(
        download_module.Path,
        "write_bytes",
        raise_os_error,
    )

    with pytest.raises(
        OSError,
        match="Error de escritura",
    ):
        download_module.download_gtfs()


def test_validate_gtfs_accepts_all_required_files_in_nested_directory(
    tmp_path,
    download_module,
):
    """Los archivos GTFS pueden estar dentro de una carpeta del ZIP."""

    zip_path = tmp_path / "nested_gtfs.zip"

    with ZipFile(zip_path, "w") as zip_file:
        for file_name in REQUIRED_FILES:
            zip_file.writestr(
                f"gtfs/{file_name}",
                "test,data\n1,example\n",
            )

    download_module.validate_gtfs(zip_path)


def test_validate_gtfs_rejects_zip_without_required_files(
    tmp_path,
    download_module,
):
    """Un ZIP válido pero sin ningún archivo GTFS obligatorio debe fallar."""

    zip_path = tmp_path / "empty_gtfs.zip"

    with ZipFile(zip_path, "w") as zip_file:
        zip_file.writestr(
            "readme.txt",
            "archivo de prueba",
        )

    with pytest.raises(
        ValueError,
        match="Faltan archivos GTFS obligatorios",
    ):
        download_module.validate_gtfs(zip_path)


def test_extract_gtfs_preserves_file_content(
    tmp_path,
    download_module,
):
    """La extracción debe conservar exactamente el contenido de los archivos."""

    zip_path = tmp_path / "gtfs.zip"

    expected_content = "stop_id,stop_name\n1,Barcelona\n"

    with ZipFile(zip_path, "w") as zip_file:
        zip_file.writestr(
            "stops.txt",
            expected_content,
        )

    extracted_dir = download_module.extract_gtfs(zip_path)

    assert (
        extracted_dir / "stops.txt"
    ).read_text() == expected_content


def test_extract_gtfs_creates_extracted_directory_only_once(
    tmp_path,
    download_module,
):
    """Extraer dos veces debe reutilizar la carpeta extracted."""

    zip_path = tmp_path / "gtfs.zip"

    create_gtfs_zip(
        zip_path,
        REQUIRED_FILES,
    )

    first_result = download_module.extract_gtfs(zip_path)
    second_result = download_module.extract_gtfs(zip_path)

    assert first_result == second_result
    assert first_result.exists()
    assert first_result.is_dir()

    for file_name in REQUIRED_FILES:
        assert (
            first_result / file_name
        ).exists()