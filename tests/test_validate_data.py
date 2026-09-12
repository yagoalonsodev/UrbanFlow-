import pandas as pd
import pytest

from ingestion.validate_data import (
    REQUIRED_FILES,
    REQUIRED_COLUMNS,
    get_latest_gtfs_directory,
    validate_files,
    validate_columns,
    validate_records,
    main,
)


def create_gtfs_files(directory):
    """
    Crea archivos GTFS mínimos válidos para las pruebas.
    """

    for file_name in REQUIRED_FILES:
        columns = REQUIRED_COLUMNS[file_name]

        dataframe = pd.DataFrame(
            [
                {
                    column: "test"
                    for column in columns
                }
            ]
        )

        dataframe.to_csv(
            directory / file_name,
            index=False,
        )


# ============================================================
# get_latest_gtfs_directory
# ============================================================


def test_get_latest_gtfs_directory_returns_latest(tmp_path, monkeypatch):
    raw_directory = tmp_path / "raw"

    old_directory = (
        raw_directory / "2026-09-09" / "extracted"
    )

    latest_directory = (
        raw_directory / "2026-09-11" / "extracted"
    )

    old_directory.mkdir(parents=True)
    latest_directory.mkdir(parents=True)

    monkeypatch.setattr(
        "ingestion.validate_data.TMB_RAW_DIR",
        raw_directory,
    )

    result = get_latest_gtfs_directory()

    assert result == latest_directory


def test_get_latest_gtfs_directory_returns_only_existing_extracted(
    tmp_path,
    monkeypatch,
):
    raw_directory = tmp_path / "raw"

    old_directory = (
        raw_directory / "2026-09-09" / "extracted"
    )

    latest_directory = raw_directory / "2026-09-11"

    old_directory.mkdir(parents=True)
    latest_directory.mkdir(parents=True)

    monkeypatch.setattr(
        "ingestion.validate_data.TMB_RAW_DIR",
        raw_directory,
    )

    with pytest.raises(
        FileNotFoundError,
        match="No se ha encontrado la carpeta extracted",
    ):
        get_latest_gtfs_directory()


def test_get_latest_gtfs_directory_no_directories(
    tmp_path,
    monkeypatch,
):
    raw_directory = tmp_path / "raw"
    raw_directory.mkdir()

    monkeypatch.setattr(
        "ingestion.validate_data.TMB_RAW_DIR",
        raw_directory,
    )

    with pytest.raises(
        FileNotFoundError,
        match="No se ha encontrado ninguna carpeta GTFS",
    ):
        get_latest_gtfs_directory()


def test_get_latest_gtfs_directory_empty_raw_directory(
    tmp_path,
    monkeypatch,
):
    raw_directory = tmp_path / "raw"
    raw_directory.mkdir()

    monkeypatch.setattr(
        "ingestion.validate_data.TMB_RAW_DIR",
        raw_directory,
    )

    with pytest.raises(FileNotFoundError):
        get_latest_gtfs_directory()


def test_get_latest_gtfs_directory_ignores_files(
    tmp_path,
    monkeypatch,
):
    raw_directory = tmp_path / "raw"
    raw_directory.mkdir()

    random_file = raw_directory / "random.txt"
    random_file.write_text("test")

    valid_directory = (
        raw_directory / "2026-09-11" / "extracted"
    )

    valid_directory.mkdir(parents=True)

    monkeypatch.setattr(
        "ingestion.validate_data.TMB_RAW_DIR",
        raw_directory,
    )

    result = get_latest_gtfs_directory()

    assert result == valid_directory


def test_get_latest_gtfs_directory_selects_latest_of_many(
    tmp_path,
    monkeypatch,
):
    raw_directory = tmp_path / "raw"

    dates = [
        "2026-09-01",
        "2026-09-05",
        "2026-09-08",
        "2026-09-10",
        "2026-09-11",
    ]

    for date in dates:
        (
            raw_directory
            / date
            / "extracted"
        ).mkdir(parents=True)

    monkeypatch.setattr(
        "ingestion.validate_data.TMB_RAW_DIR",
        raw_directory,
    )

    result = get_latest_gtfs_directory()

    assert result == (
        raw_directory
        / "2026-09-11"
        / "extracted"
    )


def test_get_latest_gtfs_directory_returns_extracted_path(
    tmp_path,
    monkeypatch,
):
    raw_directory = tmp_path / "raw"

    extracted_directory = (
        raw_directory
        / "2026-09-11"
        / "extracted"
    )

    extracted_directory.mkdir(parents=True)

    monkeypatch.setattr(
        "ingestion.validate_data.TMB_RAW_DIR",
        raw_directory,
    )

    result = get_latest_gtfs_directory()

    assert result.name == "extracted"
    assert result.parent.name == "2026-09-11"


# ============================================================
# validate_files
# ============================================================


def test_validate_files_success(tmp_path):
    create_gtfs_files(tmp_path)

    validate_files(tmp_path)


@pytest.mark.parametrize(
    "missing_file",
    sorted(REQUIRED_FILES),
)
def test_validate_files_each_required_file_missing(
    tmp_path,
    missing_file,
):
    create_gtfs_files(tmp_path)

    (tmp_path / missing_file).unlink()

    with pytest.raises(
        ValueError,
        match="Faltan archivos GTFS obligatorios",
    ):
        validate_files(tmp_path)


def test_validate_files_empty_directory(tmp_path):
    with pytest.raises(
        ValueError,
        match="Faltan archivos GTFS obligatorios",
    ):
        validate_files(tmp_path)


def test_validate_files_accepts_extra_files(tmp_path):
    create_gtfs_files(tmp_path)

    (tmp_path / "extra.txt").write_text(
        "archivo adicional"
    )

    validate_files(tmp_path)


def test_validate_files_accepts_subdirectories(tmp_path):
    create_gtfs_files(tmp_path)

    extra_directory = tmp_path / "extra"
    extra_directory.mkdir()

    validate_files(tmp_path)


def test_validate_files_does_not_require_extra_gtfs_files(
    tmp_path,
):
    create_gtfs_files(tmp_path)

    validate_files(tmp_path)


def test_validate_files_missing_multiple_files(tmp_path):
    create_gtfs_files(tmp_path)

    (tmp_path / "agency.txt").unlink()
    (tmp_path / "routes.txt").unlink()
    (tmp_path / "stops.txt").unlink()

    with pytest.raises(
        ValueError,
        match="Faltan archivos GTFS obligatorios",
    ):
        validate_files(tmp_path)


# ============================================================
# validate_columns
# ============================================================


def test_validate_columns_success(tmp_path):
    create_gtfs_files(tmp_path)

    validate_columns(tmp_path)


@pytest.mark.parametrize(
    "file_name,column",
    [
        (
            file_name,
            column,
        )
        for file_name, columns in REQUIRED_COLUMNS.items()
        for column in columns
    ],
)
def test_validate_columns_each_required_column_missing(
    tmp_path,
    file_name,
    column,
):
    create_gtfs_files(tmp_path)

    dataframe = pd.read_csv(
        tmp_path / file_name
    )

    dataframe = dataframe.drop(
        columns=[column]
    )

    dataframe.to_csv(
        tmp_path / file_name,
        index=False,
    )

    with pytest.raises(
        ValueError,
        match="no contiene las columnas obligatorias",
    ):
        validate_columns(tmp_path)


def test_validate_columns_accepts_extra_columns(
    tmp_path,
):
    create_gtfs_files(tmp_path)

    file_path = tmp_path / "routes.txt"

    dataframe = pd.read_csv(file_path)

    dataframe["extra_column"] = "extra"

    dataframe.to_csv(
        file_path,
        index=False,
    )

    validate_columns(tmp_path)


def test_validate_columns_accepts_columns_in_different_order(
    tmp_path,
):
    create_gtfs_files(tmp_path)

    file_path = tmp_path / "routes.txt"

    dataframe = pd.read_csv(file_path)

    dataframe = dataframe[
        list(reversed(dataframe.columns))
    ]

    dataframe.to_csv(
        file_path,
        index=False,
    )

    validate_columns(tmp_path)


def test_validate_columns_reads_only_required_header_data(
    tmp_path,
):
    create_gtfs_files(tmp_path)

    validate_columns(tmp_path)


def test_validate_columns_missing_all_columns(
    tmp_path,
):
    create_gtfs_files(tmp_path)

    file_path = tmp_path / "routes.txt"

    pd.DataFrame(
        {
            "wrong_column": ["test"],
        }
    ).to_csv(
        file_path,
        index=False,
    )

    with pytest.raises(
        ValueError,
        match="no contiene las columnas obligatorias",
    ):
        validate_columns(tmp_path)


def test_validate_columns_empty_csv(
    tmp_path,
):
    create_gtfs_files(tmp_path)

    file_path = tmp_path / "routes.txt"

    file_path.write_text("")

    with pytest.raises(
        (pd.errors.EmptyDataError, ValueError),
    ):
        validate_columns(tmp_path)


def test_validate_columns_only_header(
    tmp_path,
):
    create_gtfs_files(tmp_path)

    file_path = tmp_path / "routes.txt"

    columns = list(
        REQUIRED_COLUMNS["routes.txt"]
    )

    file_path.write_text(
        ",".join(columns) + "\n"
    )

    validate_columns(tmp_path)


# ============================================================
# validate_records
# ============================================================


def test_validate_records_success(tmp_path):
    create_gtfs_files(tmp_path)

    validate_records(tmp_path)


@pytest.mark.parametrize(
    "empty_file",
    sorted(REQUIRED_FILES),
)
def test_validate_records_each_empty_file(
    tmp_path,
    empty_file,
):
    create_gtfs_files(tmp_path)

    columns = list(
        REQUIRED_COLUMNS[empty_file]
    )

    empty_dataframe = pd.DataFrame(
        columns=columns
    )

    empty_dataframe.to_csv(
        tmp_path / empty_file,
        index=False,
    )

    with pytest.raises(
        ValueError,
        match="no contiene registros",
    ):
        validate_records(tmp_path)


def test_validate_records_empty_routes_file(
    tmp_path,
):
    create_gtfs_files(tmp_path)

    empty_dataframe = pd.DataFrame(
        columns=list(
            REQUIRED_COLUMNS["routes.txt"]
        )
    )

    empty_dataframe.to_csv(
        tmp_path / "routes.txt",
        index=False,
    )

    with pytest.raises(
        ValueError,
        match="no contiene registros",
    ):
        validate_records(tmp_path)


def test_validate_records_multiple_records(
    tmp_path,
):
    create_gtfs_files(tmp_path)

    file_path = tmp_path / "routes.txt"

    dataframe = pd.DataFrame(
        [
            {
                column: "test1"
                for column in REQUIRED_COLUMNS["routes.txt"]
            },
            {
                column: "test2"
                for column in REQUIRED_COLUMNS["routes.txt"]
            },
            {
                column: "test3"
                for column in REQUIRED_COLUMNS["routes.txt"]
            },
        ]
    )

    dataframe.to_csv(
        file_path,
        index=False,
    )

    validate_records(tmp_path)


def test_validate_records_single_record(
    tmp_path,
):
    create_gtfs_files(tmp_path)

    validate_records(tmp_path)


def test_validate_records_extra_columns(
    tmp_path,
):
    create_gtfs_files(tmp_path)

    file_path = tmp_path / "routes.txt"

    dataframe = pd.read_csv(file_path)

    dataframe["extra"] = "test"

    dataframe.to_csv(
        file_path,
        index=False,
    )

    validate_records(tmp_path)


def test_validate_records_missing_file(
    tmp_path,
):
    create_gtfs_files(tmp_path)

    (tmp_path / "routes.txt").unlink()

    with pytest.raises(
        FileNotFoundError,
    ):
        validate_records(tmp_path)


def test_validate_records_invalid_csv(
    tmp_path,
):
    create_gtfs_files(tmp_path)

    file_path = tmp_path / "routes.txt"

    file_path.write_text(
        '"unclosed quote,test'
    )

    with pytest.raises(
        Exception,
    ):
        validate_records(tmp_path)


# ============================================================
# main
# ============================================================


def test_main_success(
    tmp_path,
    monkeypatch,
):
    gtfs_directory = (
        tmp_path
        / "2026-09-11"
        / "extracted"
    )

    gtfs_directory.mkdir(parents=True)

    create_gtfs_files(gtfs_directory)

    monkeypatch.setattr(
        "ingestion.validate_data.get_latest_gtfs_directory",
        lambda: gtfs_directory,
    )

    monkeypatch.setattr(
        "ingestion.validate_data.validate_files",
        lambda directory: None,
    )

    monkeypatch.setattr(
        "ingestion.validate_data.validate_columns",
        lambda directory: None,
    )

    monkeypatch.setattr(
        "ingestion.validate_data.validate_records",
        lambda directory: None,
    )

    main()


def test_main_propagates_get_latest_error(
    monkeypatch,
):
    monkeypatch.setattr(
        "ingestion.validate_data.get_latest_gtfs_directory",
        lambda: (_ for _ in ()).throw(
            FileNotFoundError(
                "No GTFS"
            )
        ),
    )

    with pytest.raises(FileNotFoundError):
        main()


def test_main_propagates_validate_files_error(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        "ingestion.validate_data.get_latest_gtfs_directory",
        lambda: tmp_path,
    )

    monkeypatch.setattr(
        "ingestion.validate_data.validate_files",
        lambda directory: (_ for _ in ()).throw(
            ValueError("Archivos incorrectos")
        ),
    )

    with pytest.raises(
        ValueError,
        match="Archivos incorrectos",
    ):
        main()


def test_main_propagates_validate_columns_error(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        "ingestion.validate_data.get_latest_gtfs_directory",
        lambda: tmp_path,
    )

    monkeypatch.setattr(
        "ingestion.validate_data.validate_files",
        lambda directory: None,
    )

    monkeypatch.setattr(
        "ingestion.validate_data.validate_columns",
        lambda directory: (_ for _ in ()).throw(
            ValueError("Columnas incorrectas")
        ),
    )

    with pytest.raises(
        ValueError,
        match="Columnas incorrectas",
    ):
        main()


def test_main_propagates_validate_records_error(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        "ingestion.validate_data.get_latest_gtfs_directory",
        lambda: tmp_path,
    )

    monkeypatch.setattr(
        "ingestion.validate_data.validate_files",
        lambda directory: None,
    )

    monkeypatch.setattr(
        "ingestion.validate_data.validate_columns",
        lambda directory: None,
    )

    monkeypatch.setattr(
        "ingestion.validate_data.validate_records",
        lambda directory: (_ for _ in ()).throw(
            ValueError("Registros incorrectos")
        ),
    )

    with pytest.raises(
        ValueError,
        match="Registros incorrectos",
    ):
        main()


# ============================================================
# Integration-ish validation
# ============================================================


def test_complete_validation_pipeline(
    tmp_path,
):
    create_gtfs_files(tmp_path)

    validate_files(tmp_path)
    validate_columns(tmp_path)
    validate_records(tmp_path)


def test_complete_validation_with_extra_columns(
    tmp_path,
):
    create_gtfs_files(tmp_path)

    file_path = tmp_path / "stops.txt"

    dataframe = pd.read_csv(file_path)

    dataframe["extra_column"] = "extra"

    dataframe.to_csv(
        file_path,
        index=False,
    )

    validate_files(tmp_path)
    validate_columns(tmp_path)
    validate_records(tmp_path)


def test_complete_validation_with_multiple_records(
    tmp_path,
):
    create_gtfs_files(tmp_path)

    for file_name in REQUIRED_FILES:
        file_path = tmp_path / file_name

        columns = list(
            REQUIRED_COLUMNS[file_name]
        )

        dataframe = pd.DataFrame(
            [
                {
                    column: "value1"
                    for column in columns
                },
                {
                    column: "value2"
                    for column in columns
                },
                {
                    column: "value3"
                    for column in columns
                },
            ]
        )

        dataframe.to_csv(
            file_path,
            index=False,
        )

    validate_files(tmp_path)
    validate_columns(tmp_path)
    validate_records(tmp_path)