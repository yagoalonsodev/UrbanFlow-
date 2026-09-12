import logging
from pathlib import Path

import pandas as pd
import pytest
from ingestion import transform_gtfs

def create_integration_gtfs(tmp_path):
    """
    Creamos un GTFS pequeño para probar el pipeline completo.
    """

    gtfs_path = tmp_path / "extracted"
    gtfs_path.mkdir()

    pd.DataFrame(
        {
            "agency_id": ["A1"],
            "agency_name": [" TMB "],
        }
    ).to_csv(
        gtfs_path / "agency.txt",
        index=False,
    )

    pd.DataFrame(
        {
            "route_id": [" R1 ", "R2"],
            "route_short_name": [" 1 ", "2"],
        }
    ).to_csv(
        gtfs_path / "routes.txt",
        index=False,
    )

    pd.DataFrame(
        {
            "trip_id": [" T1 ", "T2"],
            "route_id": [" R1 ", "R2"],
            "service_id": [" S1 ", "S2"],
        }
    ).to_csv(
        gtfs_path / "trips.txt",
        index=False,
    )

    pd.DataFrame(
        {
            "stop_id": [" S1 ", "S2", "S2"],
            "stop_name": [
                " Plaça Catalunya ",
                " Sants ",
                " Sants ",
            ],
            "stop_lat": [
                "41.3874",
                "41.3797",
                "41.3797",
            ],
            "stop_lon": [
                "2.1700",
                "2.1400",
                "2.1400",
            ],
        }
    ).to_csv(
        gtfs_path / "stops.txt",
        index=False,
    )

    pd.DataFrame(
        {
            "trip_id": [" T1 ", "T1", "T2"],
            "arrival_time": [
                "08:00:00",
                "08:05:00",
                "09:00:00",
            ],
            "departure_time": [
                "08:00:00",
                "08:05:00",
                "09:00:00",
            ],
            "stop_id": [" S1 ", "S2", "S2"],
            "stop_sequence": ["1", "2", "1"],
        }
    ).to_csv(
        gtfs_path / "stop_times.txt",
        index=False,
    )

    pd.DataFrame(
        {
            "service_id": [" S1 ", "S2"],
            "monday": ["1", "1"],
            "tuesday": ["1", "1"],
            "wednesday": ["1", "1"],
            "thursday": ["1", "1"],
            "friday": ["1", "1"],
            "saturday": ["0", "0"],
            "sunday": ["0", "0"],
            "start_date": ["20260101", "20260101"],
            "end_date": ["20261231", "20261231"],
        }
    ).to_csv(
        gtfs_path / "calendar.txt",
        index=False,
    )

    return gtfs_path


# ============================================================
# load_gtfs()
# ============================================================


def test_load_gtfs_returns_all_expected_datasets(
    tmp_path,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    result = transform_gtfs.load_gtfs(
        gtfs_path
    )

    assert set(result.keys()) == {
        "agency",
        "routes",
        "trips",
        "stops",
        "stop_times",
        "calendar",
    }


def test_load_gtfs_returns_dataframes(
    tmp_path,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    result = transform_gtfs.load_gtfs(
        gtfs_path
    )

    for dataframe in result.values():
        assert isinstance(
            dataframe,
            pd.DataFrame,
        )


def test_load_gtfs_reads_expected_number_of_rows(
    tmp_path,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    result = transform_gtfs.load_gtfs(
        gtfs_path
    )

    assert len(result["agency"]) == 1
    assert len(result["routes"]) == 2
    assert len(result["trips"]) == 2
    assert len(result["stops"]) == 3
    assert len(result["stop_times"]) == 3
    assert len(result["calendar"]) == 2


def test_load_gtfs_preserves_raw_spaces(
    tmp_path,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    result = transform_gtfs.load_gtfs(
        gtfs_path
    )

    assert (
        result["routes"]
        .loc[0, "route_id"]
        == " R1 "
    )

    assert (
        result["stops"]
        .loc[0, "stop_name"]
        == " Plaça Catalunya "
    )


# ============================================================
# transform_gtfs()
# ============================================================


def test_transform_gtfs_removes_text_spaces(
    tmp_path,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    dataframes = transform_gtfs.load_gtfs(
        gtfs_path
    )

    result = transform_gtfs.transform_gtfs(
        dataframes
    )

    assert (
        result["routes"]
        .loc[0, "route_id"]
        == "R1"
    )

    assert (
        result["stops"]
        .loc[0, "stop_name"]
        == "Plaça Catalunya"
    )


def test_transform_gtfs_removes_duplicate_stops(
    tmp_path,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    dataframes = transform_gtfs.load_gtfs(
        gtfs_path
    )

    result = transform_gtfs.transform_gtfs(
        dataframes
    )

    assert len(result["stops"]) == 2


def test_transform_gtfs_keeps_first_duplicate_stop(
    tmp_path,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    dataframes = transform_gtfs.load_gtfs(
        gtfs_path
    )

    result = transform_gtfs.transform_gtfs(
        dataframes
    )

    s2 = result["stops"][
        result["stops"]["stop_id"] == "S2"
    ]

    assert len(s2) == 1
    assert s2.iloc[0]["stop_name"] == "Sants"


def test_transform_gtfs_converts_latitude_to_numeric(
    tmp_path,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    dataframes = transform_gtfs.load_gtfs(
        gtfs_path
    )

    result = transform_gtfs.transform_gtfs(
        dataframes
    )

    assert pd.api.types.is_numeric_dtype(
        result["stops"]["stop_lat"]
    )


def test_transform_gtfs_converts_longitude_to_numeric(
    tmp_path,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    dataframes = transform_gtfs.load_gtfs(
        gtfs_path
    )

    result = transform_gtfs.transform_gtfs(
        dataframes
    )

    assert pd.api.types.is_numeric_dtype(
        result["stops"]["stop_lon"]
    )


def test_transform_gtfs_converts_stop_sequence_to_numeric(
    tmp_path,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    dataframes = transform_gtfs.load_gtfs(
        gtfs_path
    )

    result = transform_gtfs.transform_gtfs(
        dataframes
    )

    assert pd.api.types.is_numeric_dtype(
        result["stop_times"][
            "stop_sequence"
        ]
    )


def test_transform_gtfs_removes_invalid_coordinates(
    tmp_path,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    stops = pd.read_csv(
        gtfs_path / "stops.txt",
        dtype=str,
    )

    stops.loc[len(stops)] = [
        "S3",
        "Parada inválida",
        "invalid",
        "invalid",
    ]

    stops.to_csv(
        gtfs_path / "stops.txt",
        index=False,
    )

    dataframes = transform_gtfs.load_gtfs(
        gtfs_path
    )

    result = transform_gtfs.transform_gtfs(
        dataframes
    )

    assert (
        "S3"
        not in result["stops"]["stop_id"].values
    )


def test_transform_gtfs_removes_empty_identifiers(
    tmp_path,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    routes = pd.read_csv(
        gtfs_path / "routes.txt",
        dtype=str,
    )

    routes.loc[len(routes)] = [
        "",
        "99",
    ]

    routes.to_csv(
        gtfs_path / "routes.txt",
        index=False,
    )

    dataframes = transform_gtfs.load_gtfs(
        gtfs_path
    )

    result = transform_gtfs.transform_gtfs(
        dataframes
    )

    assert len(result["routes"]) == 2


def test_transform_gtfs_converts_empty_strings_to_null(
    tmp_path,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    routes = pd.read_csv(
        gtfs_path / "routes.txt",
        dtype=str,
    )

    routes.loc[
        0,
        "route_short_name",
    ] = "   "

    routes.to_csv(
        gtfs_path / "routes.txt",
        index=False,
    )

    dataframes = transform_gtfs.load_gtfs(
        gtfs_path
    )

    result = transform_gtfs.transform_gtfs(
        dataframes
    )

    assert pd.isna(
        result["routes"].loc[
            0,
            "route_short_name",
        ]
    )


def test_transform_gtfs_removes_complete_duplicate_rows(
    tmp_path,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    routes = pd.read_csv(
        gtfs_path / "routes.txt",
        dtype=str,
    )

    routes = pd.concat(
        [
            routes,
            routes.iloc[[0]],
        ],
        ignore_index=True,
    )

    routes.to_csv(
        gtfs_path / "routes.txt",
        index=False,
    )

    dataframes = transform_gtfs.load_gtfs(
        gtfs_path
    )

    result = transform_gtfs.transform_gtfs(
        dataframes
    )

    assert len(result["routes"]) == 2


# ============================================================
# Raw data protection
# ============================================================


def test_transform_gtfs_does_not_modify_routes_raw_data(
    tmp_path,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    dataframes = transform_gtfs.load_gtfs(
        gtfs_path
    )

    original = dataframes[
        "routes"
    ].copy()

    transform_gtfs.transform_gtfs(
        dataframes
    )

    assert dataframes["routes"].equals(
        original
    )


def test_transform_gtfs_does_not_modify_stops_raw_data(
    tmp_path,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    dataframes = transform_gtfs.load_gtfs(
        gtfs_path
    )

    original = dataframes[
        "stops"
    ].copy()

    transform_gtfs.transform_gtfs(
        dataframes
    )

    assert dataframes["stops"].equals(
        original
    )


def test_transform_gtfs_returns_new_dictionary(
    tmp_path,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    dataframes = transform_gtfs.load_gtfs(
        gtfs_path
    )

    result = transform_gtfs.transform_gtfs(
        dataframes
    )

    assert result is not dataframes


def test_transform_gtfs_returns_new_dataframes(
    tmp_path,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    dataframes = transform_gtfs.load_gtfs(
        gtfs_path
    )

    result = transform_gtfs.transform_gtfs(
        dataframes
    )

    for name in dataframes:
        assert result[name] is not dataframes[name]


# ============================================================
# save_processed_data()
# ============================================================


def test_save_processed_data_creates_output_directory(
    tmp_path,
    monkeypatch,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    processed_directory = (
        tmp_path / "processed"
    )

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_PROCESSED_DIR",
        processed_directory,
    )

    dataframes = transform_gtfs.transform_gtfs(
        transform_gtfs.load_gtfs(
            gtfs_path
        )
    )

    transform_gtfs.save_processed_data(
        dataframes,
        "2026-09-11",
    )

    assert (
        processed_directory
        / "2026-09-11"
    ).is_dir()


def test_save_processed_data_creates_all_csv_files(
    tmp_path,
    monkeypatch,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    processed_directory = (
        tmp_path / "processed"
    )

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_PROCESSED_DIR",
        processed_directory,
    )

    dataframes = transform_gtfs.transform_gtfs(
        transform_gtfs.load_gtfs(
            gtfs_path
        )
    )

    transform_gtfs.save_processed_data(
        dataframes,
        "2026-09-11",
    )

    output_directory = (
        processed_directory
        / "2026-09-11"
    )

    expected_files = {
        "agency.csv",
        "routes.csv",
        "trips.csv",
        "stops.csv",
        "stop_times.csv",
        "calendar.csv",
    }

    generated_files = {
        file.name
        for file in output_directory.glob(
            "*.csv"
        )
    }

    assert generated_files == expected_files


def test_save_processed_data_preserves_row_counts(
    tmp_path,
    monkeypatch,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    processed_directory = (
        tmp_path / "processed"
    )

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_PROCESSED_DIR",
        processed_directory,
    )

    dataframes = transform_gtfs.transform_gtfs(
        transform_gtfs.load_gtfs(
            gtfs_path
        )
    )

    transform_gtfs.save_processed_data(
        dataframes,
        "2026-09-11",
    )

    output_directory = (
        processed_directory
        / "2026-09-11"
    )

    assert len(
        pd.read_csv(
            output_directory
            / "agency.csv"
        )
    ) == len(dataframes["agency"])

    assert len(
        pd.read_csv(
            output_directory
            / "routes.csv"
        )
    ) == len(dataframes["routes"])

    assert len(
        pd.read_csv(
            output_directory
            / "stops.csv"
        )
    ) == len(dataframes["stops"])

    assert len(
        pd.read_csv(
            output_directory
            / "trips.csv"
        )
    ) == len(dataframes["trips"])


def test_save_processed_data_preserves_route_ids(
    tmp_path,
    monkeypatch,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    processed_directory = (
        tmp_path / "processed"
    )

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_PROCESSED_DIR",
        processed_directory,
    )

    dataframes = transform_gtfs.transform_gtfs(
        transform_gtfs.load_gtfs(
            gtfs_path
        )
    )

    transform_gtfs.save_processed_data(
        dataframes,
        "2026-09-11",
    )

    saved_routes = pd.read_csv(
        processed_directory
        / "2026-09-11"
        / "routes.csv"
    )

    assert set(
        saved_routes["route_id"]
    ) == {
        "R1",
        "R2",
    }


def test_save_processed_data_preserves_stop_ids(
    tmp_path,
    monkeypatch,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    processed_directory = (
        tmp_path / "processed"
    )

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_PROCESSED_DIR",
        processed_directory,
    )

    dataframes = transform_gtfs.transform_gtfs(
        transform_gtfs.load_gtfs(
            gtfs_path
        )
    )

    transform_gtfs.save_processed_data(
        dataframes,
        "2026-09-11",
    )

    saved_stops = pd.read_csv(
        processed_directory
        / "2026-09-11"
        / "stops.csv"
    )

    assert set(
        saved_stops["stop_id"]
    ) == {
        "S1",
        "S2",
    }


def test_save_processed_data_can_be_loaded_again(
    tmp_path,
    monkeypatch,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    processed_directory = (
        tmp_path / "processed"
    )

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_PROCESSED_DIR",
        processed_directory,
    )

    dataframes = transform_gtfs.transform_gtfs(
        transform_gtfs.load_gtfs(
            gtfs_path
        )
    )

    transform_gtfs.save_processed_data(
        dataframes,
        "2026-09-11",
    )

    output_directory = (
        processed_directory
        / "2026-09-11"
    )

    for name in dataframes:
        file_path = (
            output_directory
            / f"{name}.csv"
        )

        loaded = pd.read_csv(
            file_path
        )

        assert isinstance(
            loaded,
            pd.DataFrame,
        )


def test_save_processed_data_does_not_create_extra_files(
    tmp_path,
    monkeypatch,
):
    gtfs_path = create_integration_gtfs(tmp_path)

    processed_directory = (
        tmp_path / "processed"
    )

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_PROCESSED_DIR",
        processed_directory,
    )

    dataframes = transform_gtfs.transform_gtfs(
        transform_gtfs.load_gtfs(
            gtfs_path
        )
    )

    transform_gtfs.save_processed_data(
        dataframes,
        "2026-09-11",
    )

    output_directory = (
        processed_directory
        / "2026-09-11"
    )

    files = list(
        output_directory.iterdir()
    )

    assert len(files) == 6

    assert all(
        file.suffix == ".csv"
        for file in files
    )


# ============================================================
# Pipeline completo
# ============================================================


def test_complete_pipeline(
    tmp_path,
    monkeypatch,
):
    """
    Probamos todo el flujo:

    TXT → load → transform → save → CSV
    """

    gtfs_path = create_integration_gtfs(
        tmp_path
    )

    processed_directory = (
        tmp_path / "processed"
    )

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_PROCESSED_DIR",
        processed_directory,
    )

    dataframes = transform_gtfs.load_gtfs(
        gtfs_path
    )

    transformed = transform_gtfs.transform_gtfs(
        dataframes
    )

    transform_gtfs.save_processed_data(
        transformed,
        "2026-09-11",
    )

    output_directory = (
        processed_directory
        / "2026-09-11"
    )

    assert (
        output_directory.exists()
    )

    saved_stops = pd.read_csv(
        output_directory
        / "stops.csv"
    )

    saved_routes = pd.read_csv(
        output_directory
        / "routes.csv"
    )

    assert len(saved_stops) == 2
    assert len(saved_routes) == 2

    assert set(
        saved_stops["stop_id"]
    ) == {
        "S1",
        "S2",
    }

    assert set(
        saved_routes["route_id"]
    ) == {
        "R1",
        "R2",
    }


def test_complete_pipeline_can_run_twice(
    tmp_path,
    monkeypatch,
):
    """
    Comprobamos que ejecutar el pipeline
    dos veces no rompe los datos.
    """

    gtfs_path = create_integration_gtfs(
        tmp_path
    )

    processed_directory = (
        tmp_path / "processed"
    )

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_PROCESSED_DIR",
        processed_directory,
    )

    for _ in range(2):
        dataframes = transform_gtfs.load_gtfs(
            gtfs_path
        )

        transformed = (
            transform_gtfs.transform_gtfs(
                dataframes
            )
        )

        transform_gtfs.save_processed_data(
            transformed,
            "2026-09-11",
        )

    saved_stops = pd.read_csv(
        processed_directory
        / "2026-09-11"
        / "stops.csv"
    )

    assert len(saved_stops) == 2


def test_complete_pipeline_output_contains_no_duplicate_stops(
    tmp_path,
    monkeypatch,
):
    gtfs_path = create_integration_gtfs(
        tmp_path
    )

    processed_directory = (
        tmp_path / "processed"
    )

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_PROCESSED_DIR",
        processed_directory,
    )

    dataframes = transform_gtfs.load_gtfs(
        gtfs_path
    )

    transformed = transform_gtfs.transform_gtfs(
        dataframes
    )

    transform_gtfs.save_processed_data(
        transformed,
        "2026-09-11",
    )

    saved_stops = pd.read_csv(
        processed_directory
        / "2026-09-11"
        / "stops.csv"
    )

    assert (
        saved_stops["stop_id"]
        .duplicated()
        .sum()
        == 0
    )


def test_complete_pipeline_output_contains_no_null_stop_coordinates(
    tmp_path,
    monkeypatch,
):
    gtfs_path = create_integration_gtfs(
        tmp_path
    )

    processed_directory = (
        tmp_path / "processed"
    )

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_PROCESSED_DIR",
        processed_directory,
    )

    dataframes = transform_gtfs.load_gtfs(
        gtfs_path
    )

    transformed = transform_gtfs.transform_gtfs(
        dataframes
    )

    transform_gtfs.save_processed_data(
        transformed,
        "2026-09-11",
    )

    saved_stops = pd.read_csv(
        processed_directory
        / "2026-09-11"
        / "stops.csv"
    )

    assert (
        saved_stops["stop_lat"]
        .isna()
        .sum()
        == 0
    )

    assert (
        saved_stops["stop_lon"]
        .isna()
        .sum()
        == 0
    )


def test_complete_pipeline_output_contains_numeric_coordinates(
    tmp_path,
    monkeypatch,
):
    gtfs_path = create_integration_gtfs(
        tmp_path
    )

    processed_directory = (
        tmp_path / "processed"
    )

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_PROCESSED_DIR",
        processed_directory,
    )

    dataframes = transform_gtfs.load_gtfs(
        gtfs_path
    )

    transformed = transform_gtfs.transform_gtfs(
        dataframes
    )

    transform_gtfs.save_processed_data(
        transformed,
        "2026-09-11",
    )

    saved_stops = pd.read_csv(
        processed_directory
        / "2026-09-11"
        / "stops.csv"
    )

    assert pd.api.types.is_numeric_dtype(
        saved_stops["stop_lat"]
    )

    assert pd.api.types.is_numeric_dtype(
        saved_stops["stop_lon"]
    )


# ============================================================
# Logs
# ============================================================


def test_complete_pipeline_logs_loading(
    tmp_path,
    caplog,
):
    caplog.set_level(logging.INFO)

    gtfs_path = create_integration_gtfs(
        tmp_path
    )

    transform_gtfs.load_gtfs(
        gtfs_path
    )

    assert "Cargando archivos GTFS..." in (
        caplog.text
    )

def test_complete_pipeline_logs_transformation(
    tmp_path,
    caplog,
):
    caplog.set_level(logging.INFO)
    gtfs_path = create_integration_gtfs(
        tmp_path
    )

    dataframes = transform_gtfs.load_gtfs(
        gtfs_path
    )

    transform_gtfs.transform_gtfs(
        dataframes
    )

    assert "Iniciando transformaciones..." in (
        caplog.text
    )

    assert (
        "Transformaciones completadas correctamente."
        in caplog.text
    )


def test_complete_pipeline_logs_saving(
    tmp_path,
    monkeypatch,
    caplog,
):
    caplog.set_level(logging.INFO)
    gtfs_path = create_integration_gtfs(
        tmp_path
    )

    processed_directory = (
        tmp_path / "processed"
    )

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_PROCESSED_DIR",
        processed_directory,
    )

    dataframes = transform_gtfs.load_gtfs(
        gtfs_path
    )

    transformed = transform_gtfs.transform_gtfs(
        dataframes
    )

    transform_gtfs.save_processed_data(
        transformed,
        "2026-09-11",
    )

    assert (
        "Guardando datos transformados"
        in caplog.text
    )


def test_complete_pipeline_logs_duplicate_removal(
    tmp_path,
    caplog,
):
    caplog.set_level(logging.INFO)
    gtfs_path = create_integration_gtfs(
        tmp_path
    )

    dataframes = transform_gtfs.load_gtfs(
        gtfs_path
    )

    transform_gtfs.transform_gtfs(
        dataframes
    )

    assert (
        "stop_id duplicados eliminados"
        in caplog.text
    )


# ============================================================
# Error handling
# ============================================================


def test_load_gtfs_raises_when_file_is_missing(
    tmp_path,
):
    gtfs_path = tmp_path / "extracted"
    gtfs_path.mkdir()

    with pytest.raises(
        FileNotFoundError
    ):
        transform_gtfs.load_gtfs(
            gtfs_path
        )


def test_pipeline_fails_when_stops_file_is_missing(
    tmp_path,
):
    gtfs_path = create_integration_gtfs(
        tmp_path
    )

    (
        gtfs_path / "stops.txt"
    ).unlink()

    with pytest.raises(
        FileNotFoundError
    ):
        transform_gtfs.load_gtfs(
            gtfs_path
        )


def test_pipeline_fails_when_routes_file_is_missing(
    tmp_path,
):
    gtfs_path = create_integration_gtfs(
        tmp_path
    )

    (
        gtfs_path / "routes.txt"
    ).unlink()

    with pytest.raises(
        FileNotFoundError
    ):
        transform_gtfs.load_gtfs(
            gtfs_path
        )


def test_pipeline_fails_when_calendar_file_is_missing(
    tmp_path,
):
    gtfs_path = create_integration_gtfs(
        tmp_path
    )

    (
        gtfs_path / "calendar.txt"
    ).unlink()

    with pytest.raises(
        FileNotFoundError
    ):
        transform_gtfs.load_gtfs(
            gtfs_path
        )
