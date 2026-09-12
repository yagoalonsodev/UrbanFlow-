import logging
from pathlib import Path

import pandas as pd
import pytest

from ingestion import transform_gtfs


# ============================================================
# HELPERS
# ============================================================


def create_minimal_gtfs_data():
    return {
        "agency": pd.DataFrame(
            {
                "agency_name": [" TMB ", "Metro"],
                "agency_url": ["https://tmb.cat", "https://metro.cat"],
            }
        ),
        "routes": pd.DataFrame(
            {
                "route_id": [" R1 ", "R2"],
                "route_short_name": [" 1 ", "2"],
            }
        ),
        "trips": pd.DataFrame(
            {
                "trip_id": [" T1 ", "T2"],
                "route_id": [" R1 ", "R2"],
                "service_id": [" S1 ", "S2"],
            }
        ),
        "stops": pd.DataFrame(
            {
                "stop_id": [" S1 ", "S2"],
                "stop_name": [" Stop 1 ", "Stop 2"],
                "stop_lat": ["41.39", "41.40"],
                "stop_lon": ["2.17", "2.18"],
            }
        ),
        "stop_times": pd.DataFrame(
            {
                "trip_id": [" T1 ", "T2"],
                "stop_id": [" S1 ", "S2"],
                "arrival_time": ["10:00:00", "11:00:00"],
                "stop_sequence": ["1", "2"],
            }
        ),
        "calendar": pd.DataFrame(
            {
                "service_id": [" S1 ", "S2"],
                "monday": ["1", "1"],
            }
        ),
    }


def create_gtfs_files(directory: Path):
    dataframes = create_minimal_gtfs_data()

    for name, dataframe in dataframes.items():
        dataframe.to_csv(
            directory / f"{name}.txt",
            index=False,
        )


def create_gtfs_dataframe():
    return create_minimal_gtfs_data()


# ============================================================
# get_latest_gtfs()
# ============================================================


def test_get_latest_gtfs_raises_when_raw_directory_does_not_exist(
    tmp_path,
    monkeypatch,
):
    raw_directory = tmp_path / "raw"

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_RAW_DIR",
        raw_directory,
    )

    with pytest.raises(FileNotFoundError):
        transform_gtfs.get_latest_gtfs()


def test_get_latest_gtfs_raises_when_no_gtfs_exists(
    tmp_path,
    monkeypatch,
):
    raw_directory = tmp_path / "raw"
    raw_directory.mkdir()

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_RAW_DIR",
        raw_directory,
    )

    with pytest.raises(
        FileNotFoundError,
        match="No se ha encontrado ningún GTFS descargado",
    ):
        transform_gtfs.get_latest_gtfs()


def test_get_latest_gtfs_raises_when_extracted_directory_is_missing(
    tmp_path,
    monkeypatch,
):
    raw_directory = tmp_path / "raw"
    raw_directory.mkdir()

    (raw_directory / "2026-09-10").mkdir()

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_RAW_DIR",
       raw_directory,
    )

    with pytest.raises(FileNotFoundError):
        transform_gtfs.get_latest_gtfs()


def test_get_latest_gtfs_returns_latest_directory(
    tmp_path,
    monkeypatch,
):
    raw_directory = tmp_path / "raw"

    old_directory = (
        raw_directory
        / "2026-09-09"
        / "extracted"
    )

    latest_directory = (
        raw_directory
        / "2026-09-11"
        / "extracted"
    )

    old_directory.mkdir(parents=True)
    latest_directory.mkdir(parents=True)

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_RAW_DIR",
        raw_directory,
    )

    result = transform_gtfs.get_latest_gtfs()

    assert result == latest_directory


def test_get_latest_gtfs_ignores_directories_without_extracted(
    tmp_path,
    monkeypatch,
):
    raw_directory = tmp_path / "raw"

    invalid_directory = raw_directory / "2026-09-12"
    valid_directory = (
        raw_directory
        / "2026-09-11"
        / "extracted"
    )

    invalid_directory.mkdir(parents=True)
    valid_directory.mkdir(parents=True)

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_RAW_DIR",
        raw_directory,
    )

    result = transform_gtfs.get_latest_gtfs()

    assert result == valid_directory


# ============================================================
# load_gtfs()
# ============================================================


def test_load_gtfs_reads_all_datasets(tmp_path):
    create_gtfs_files(tmp_path)

    result = transform_gtfs.load_gtfs(tmp_path)

    expected_datasets = {
        "agency",
        "routes",
        "trips",
        "stops",
        "stop_times",
        "calendar",
    }

    assert set(result.keys()) == expected_datasets


def test_load_gtfs_reads_expected_route_values(tmp_path):
    create_gtfs_files(tmp_path)

    result = transform_gtfs.load_gtfs(tmp_path)

    assert result["routes"]["route_id"].tolist() == [
        " R1 ",
        "R2",
    ]


def test_load_gtfs_reads_expected_stop_values(tmp_path):
    create_gtfs_files(tmp_path)

    result = transform_gtfs.load_gtfs(tmp_path)

    assert result["stops"]["stop_id"].tolist() == [
        " S1 ",
        "S2",
    ]


def test_load_gtfs_reads_values_as_strings(tmp_path):
    create_gtfs_files(tmp_path)

    result = transform_gtfs.load_gtfs(tmp_path)

    assert str(
        result["routes"]["route_id"].dtype
    ) in {
        "object",
        "str",
        "string",
    }

    assert str(
        result["stops"]["stop_id"].dtype
    ) in {
        "object",
        "str",
        "string",
    }


def test_load_gtfs_raises_when_file_is_missing(tmp_path):
    create_gtfs_files(tmp_path)

    (tmp_path / "routes.txt").unlink()

    with pytest.raises(FileNotFoundError):
        transform_gtfs.load_gtfs(tmp_path)


# ============================================================
# transform_gtfs()
# ============================================================


def test_transform_gtfs_strips_column_names():
    dataframes = create_minimal_gtfs_data()

    dataframes["routes"].columns = [
        " route_id ",
        " route_short_name ",
    ]

    result = transform_gtfs.transform_gtfs(dataframes)

    assert list(result["routes"].columns) == [
        "route_id",
        "route_short_name",
    ]


def test_transform_gtfs_strips_text_values():
    dataframes = create_minimal_gtfs_data()

    result = transform_gtfs.transform_gtfs(dataframes)

    assert result["routes"].loc[0, "route_id"] == "R1"
    assert result["routes"].loc[0, "route_short_name"] == "1"
    assert result["stops"].loc[0, "stop_name"] == "Stop 1"


def test_transform_gtfs_converts_empty_strings_to_nulls():
    dataframes = create_minimal_gtfs_data()

    dataframes["routes"].loc[
        0,
        "route_short_name",
    ] = "   "

    result = transform_gtfs.transform_gtfs(dataframes)

    assert pd.isna(
        result["routes"].loc[
            0,
            "route_short_name",
        ]
    )


def test_transform_gtfs_converts_stop_coordinates_to_numeric():
    dataframes = create_minimal_gtfs_data()

    result = transform_gtfs.transform_gtfs(dataframes)

    assert pd.api.types.is_numeric_dtype(
        result["stops"]["stop_lat"]
    )

    assert pd.api.types.is_numeric_dtype(
        result["stops"]["stop_lon"]
    )

    assert result["stops"].loc[
        0,
        "stop_lat",
    ] == pytest.approx(41.39)

    assert result["stops"].loc[
        0,
        "stop_lon",
    ] == pytest.approx(2.17)


def test_transform_gtfs_invalid_coordinates_are_removed():
    dataframes = create_minimal_gtfs_data()

    dataframes["stops"].loc[
        0,
        "stop_lat",
    ] = "invalid"

    result = transform_gtfs.transform_gtfs(dataframes)

    assert "S1" not in (
        result["stops"]["stop_id"].values
    )

    assert len(result["stops"]) == 1


def test_transform_gtfs_converts_stop_sequence_to_numeric():
    dataframes = create_minimal_gtfs_data()

    result = transform_gtfs.transform_gtfs(dataframes)

    assert pd.api.types.is_numeric_dtype(
        result["stop_times"]["stop_sequence"]
    )

    assert result["stop_times"].loc[
        0,
        "stop_sequence",
    ] == 1


def test_transform_gtfs_invalid_stop_sequence_becomes_null():
    dataframes = create_minimal_gtfs_data()

    dataframes["stop_times"].loc[
        0,
        "stop_sequence",
    ] = "invalid"

    result = transform_gtfs.transform_gtfs(dataframes)

    assert pd.isna(
        result["stop_times"].loc[
            0,
            "stop_sequence",
        ]
    )


def test_transform_gtfs_removes_duplicate_rows():
    dataframes = create_minimal_gtfs_data()

    duplicate_route = dataframes["routes"].iloc[
        [0]
    ].copy()

    dataframes["routes"] = pd.concat(
        [
            dataframes["routes"],
            duplicate_route,
        ],
        ignore_index=True,
    )

    result = transform_gtfs.transform_gtfs(dataframes)

    assert len(result["routes"]) == 2


def test_transform_gtfs_removes_duplicate_stop_ids():
    dataframes = create_minimal_gtfs_data()

    duplicate_stop = dataframes["stops"].iloc[
        [0]
    ].copy()

    duplicate_stop["stop_name"] = "Another name"

    dataframes["stops"] = pd.concat(
        [
            dataframes["stops"],
            duplicate_stop,
        ],
        ignore_index=True,
    )

    result = transform_gtfs.transform_gtfs(dataframes)

    assert len(result["stops"]) == 2
    assert result["stops"]["stop_id"].is_unique


def test_transform_gtfs_keeps_first_duplicate_stop():
    dataframes = create_minimal_gtfs_data()

    duplicate_stop = dataframes["stops"].iloc[
        [0]
    ].copy()

    duplicate_stop["stop_name"] = "Another name"

    dataframes["stops"] = pd.concat(
        [
            dataframes["stops"],
            duplicate_stop,
        ],
        ignore_index=True,
    )

    result = transform_gtfs.transform_gtfs(dataframes)

    assert result["stops"].iloc[
        0
    ]["stop_name"] == "Stop 1"


def test_transform_gtfs_removes_rows_without_route_id():
    dataframes = create_minimal_gtfs_data()

    dataframes["routes"].loc[
        len(dataframes["routes"])
    ] = [
        pd.NA,
        "Invalid",
    ]

    result = transform_gtfs.transform_gtfs(dataframes)

    assert result["routes"]["route_id"].notna().all()
    assert len(result["routes"]) == 2


def test_transform_gtfs_removes_rows_without_trip_id():
    dataframes = create_minimal_gtfs_data()

    dataframes["trips"].loc[
        len(dataframes["trips"])
    ] = [
        pd.NA,
        "R1",
        "S1",
    ]

    result = transform_gtfs.transform_gtfs(dataframes)

    assert result["trips"]["trip_id"].notna().all()
    assert len(result["trips"]) == 2


def test_transform_gtfs_removes_rows_without_stop_id():
    dataframes = create_minimal_gtfs_data()

    dataframes["stops"].loc[
        len(dataframes["stops"])
    ] = [
        pd.NA,
        "Invalid",
        41.39,
        2.17,
    ]

    result = transform_gtfs.transform_gtfs(dataframes)

    assert result["stops"]["stop_id"].notna().all()
    assert len(result["stops"]) == 2


def test_transform_gtfs_removes_rows_without_stop_times_identifiers():
    dataframes = create_minimal_gtfs_data()

    dataframes["stop_times"].loc[
        len(dataframes["stop_times"])
    ] = [
        pd.NA,
        "S1",
        "10:00:00",
        3,
    ]

    result = transform_gtfs.transform_gtfs(dataframes)

    assert result["stop_times"][
        "trip_id"
    ].notna().all()

    assert result["stop_times"][
        "stop_id"
    ].notna().all()

    assert len(result["stop_times"]) == 2


def test_transform_gtfs_removes_rows_without_service_id():
    dataframes = create_minimal_gtfs_data()

    dataframes["calendar"].loc[
        len(dataframes["calendar"])
    ] = [
        pd.NA,
        "1",
    ]

    result = transform_gtfs.transform_gtfs(dataframes)

    assert result["calendar"][
        "service_id"
    ].notna().all()

    assert len(result["calendar"]) == 2


def test_transform_gtfs_removes_stops_without_coordinates():
    dataframes = create_minimal_gtfs_data()

    dataframes["stops"].loc[
        len(dataframes["stops"])
    ] = [
        "S3",
        "No coordinates",
        pd.NA,
        2.19,
    ]

    result = transform_gtfs.transform_gtfs(dataframes)

    assert result["stops"][
        "stop_lat"
    ].notna().all()

    assert result["stops"][
        "stop_lon"
    ].notna().all()

    assert len(result["stops"]) == 2


def test_transform_gtfs_removes_stops_without_longitude():
    dataframes = create_minimal_gtfs_data()

    dataframes["stops"].loc[
        len(dataframes["stops"])
    ] = [
        "S3",
        "No longitude",
        41.39,
        pd.NA,
    ]

    result = transform_gtfs.transform_gtfs(dataframes)

    assert result["stops"][
        "stop_lon"
    ].notna().all()

    assert len(result["stops"]) == 2


def test_transform_gtfs_does_not_modify_original_dataframes():
    dataframes = create_minimal_gtfs_data()

    original_routes = dataframes["routes"].copy(
        deep=True
    )

    transform_gtfs.transform_gtfs(dataframes)

    pd.testing.assert_frame_equal(
        dataframes["routes"],
        original_routes,
    )


def test_transform_gtfs_preserves_all_dataset_names():
    dataframes = create_minimal_gtfs_data()

    result = transform_gtfs.transform_gtfs(dataframes)

    assert set(result.keys()) == set(
        dataframes.keys()
    )


def test_transform_gtfs_removes_multiple_invalid_rows():
    dataframes = create_minimal_gtfs_data()

    dataframes["routes"] = pd.concat(
        [
            dataframes["routes"],
            pd.DataFrame(
                {
                    "route_id": [
                        pd.NA,
                        pd.NA,
                    ],
                    "route_short_name": [
                        "X",
                        "Y",
                    ],
                }
            ),
        ],
        ignore_index=True,
    )

    result = transform_gtfs.transform_gtfs(dataframes)

    assert len(result["routes"]) == 2
    assert result["routes"][
        "route_id"
    ].notna().all()


# ============================================================
# save_processed_data()
# ============================================================


def test_save_processed_data_creates_date_directory(
    tmp_path,
    monkeypatch,
):
    processed_directory = (
        tmp_path / "processed"
    )

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_PROCESSED_DIR",
        processed_directory,
    )

    dataframes = create_minimal_gtfs_data()

    transform_gtfs.save_processed_data(
        dataframes,
        "2026-09-11",
    )

    output_directory = (
        processed_directory
        / "2026-09-11"
    )

    assert output_directory.exists()
    assert output_directory.is_dir()


def test_save_processed_data_creates_one_csv_per_dataset(
    tmp_path,
    monkeypatch,
):
    processed_directory = (
        tmp_path / "processed"
    )

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_PROCESSED_DIR",
        processed_directory,
    )

    dataframes = create_minimal_gtfs_data()

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

    assert {
        file.name
        for file in output_directory.glob(
            "*.csv"
        )
    } == expected_files


def test_save_processed_data_preserves_dataframe_content(
    tmp_path,
    monkeypatch,
):
    processed_directory = (
        tmp_path / "processed"
    )

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_PROCESSED_DIR",
        processed_directory,
    )

    dataframes = create_minimal_gtfs_data()

    transform_gtfs.save_processed_data(
        dataframes,
        "2026-09-11",
    )

    saved_routes = pd.read_csv(
        processed_directory
        / "2026-09-11"
        / "routes.csv"
    )

    assert saved_routes[
        "route_id"
    ].tolist() == [
        " R1 ",
        "R2",
    ]

    assert saved_routes[
        "route_short_name"
    ].tolist() == [1, 2]


def test_save_processed_data_overwrites_existing_files(
    tmp_path,
    monkeypatch,
):
    processed_directory = (
        tmp_path / "processed"
    )

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_PROCESSED_DIR",
        processed_directory,
    )

    dataframes = create_minimal_gtfs_data()

    transform_gtfs.save_processed_data(
        dataframes,
        "2026-09-11",
    )

    dataframes["routes"] = pd.DataFrame(
        {
            "route_id": ["NEW"],
            "route_short_name": ["99"],
        }
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

    assert saved_routes[
        "route_id"
    ].tolist() == ["NEW"]


def test_save_processed_data_creates_nested_directory(
    tmp_path,
    monkeypatch,
):
    processed_directory = (
        tmp_path / "processed"
    )

    monkeypatch.setattr(
        transform_gtfs,
        "TMB_PROCESSED_DIR",
        processed_directory,
    )

    dataframes = create_minimal_gtfs_data()

    transform_gtfs.save_processed_data(
        dataframes,
        "2026-09-11",
    )

    assert (
        processed_directory
        / "2026-09-11"
        / "agency.csv"
    ).exists()


# ============================================================
# analyze_final_data()
# ============================================================


def test_analyze_final_data_runs_successfully(
    caplog,
):
    dataframes = create_minimal_gtfs_data()

    with caplog.at_level(logging.INFO):
        transform_gtfs.analyze_final_data(
            dataframes
        )

    assert (
        "ANÁLISIS FINAL DE LOS DATOS"
        in caplog.text
    )

    assert (
        "ANÁLISIS FINAL COMPLETADO CORRECTAMENTE"
        in caplog.text
    )


def test_analyze_final_data_reports_duplicate_stop_ids(
    caplog,
):
    dataframes = create_minimal_gtfs_data()

    dataframes["stops"] = pd.concat(
        [
            dataframes["stops"],
            dataframes["stops"].iloc[[0]],
        ],
        ignore_index=True,
    )

    with caplog.at_level(logging.INFO):
        transform_gtfs.analyze_final_data(
            dataframes
        )

    assert (
        "stop_id duplicados finales: 1"
        in caplog.text
    )


def test_analyze_final_data_reports_record_counts(
    caplog,
):
    dataframes = create_minimal_gtfs_data()

    with caplog.at_level(logging.INFO):
        transform_gtfs.analyze_final_data(
            dataframes
        )

    assert (
        "Registros finales: 2"
        in caplog.text
    )


def test_analyze_final_data_reports_null_values(
    caplog,
):
    dataframes = create_minimal_gtfs_data()

    dataframes["routes"].loc[
        0,
        "route_short_name",
    ] = pd.NA

    with caplog.at_level(logging.INFO):
        transform_gtfs.analyze_final_data(
            dataframes
        )

    assert (
        "Valores nulos finales: 1"
        in caplog.text
    )


def test_analyze_final_data_reports_no_duplicate_rows(
    caplog,
):
    dataframes = create_minimal_gtfs_data()

    with caplog.at_level(logging.INFO):
        transform_gtfs.analyze_final_data(
            dataframes
        )

    assert (
        "Registros duplicados finales: 0"
        in caplog.text
    )


# ============================================================
# main()
# ============================================================


def test_main_executes_complete_pipeline(
    monkeypatch,
):
    calls = []

    dataframes = create_minimal_gtfs_data()

    gtfs_path = Path(
        "/tmp/2026-09-11/extracted"
    )

    def mock_get_latest_gtfs():
        calls.append(
            "get_latest_gtfs"
        )
        return gtfs_path

    def mock_load_gtfs(path):
        calls.append(
            ("load_gtfs", path)
        )
        return dataframes

    def mock_transform_gtfs(
        input_dataframes,
    ):
        calls.append(
            "transform_gtfs"
        )
        return input_dataframes

    def mock_save_processed_data(
        input_dataframes,
        date,
    ):
        calls.append(
            (
                "save_processed_data",
                date,
            )
        )

    def mock_analyze_final_data(
        input_dataframes,
    ):
        calls.append(
            "analyze_final_data"
        )

    monkeypatch.setattr(
        transform_gtfs,
        "get_latest_gtfs",
        mock_get_latest_gtfs,
    )

    monkeypatch.setattr(
        transform_gtfs,
        "load_gtfs",
        mock_load_gtfs,
    )

    monkeypatch.setattr(
        transform_gtfs,
        "transform_gtfs",
        mock_transform_gtfs,
    )

    monkeypatch.setattr(
        transform_gtfs,
        "save_processed_data",
        mock_save_processed_data,
    )

    monkeypatch.setattr(
        transform_gtfs,
        "analyze_final_data",
        mock_analyze_final_data,
    )

    transform_gtfs.main()

    assert calls == [
        "get_latest_gtfs",
        (
            "load_gtfs",
            gtfs_path,
        ),
        "transform_gtfs",
        (
            "save_processed_data",
            "2026-09-11",
        ),
        "analyze_final_data",
    ]


def test_main_propagates_file_not_found_error(
    monkeypatch,
):
    def mock_get_latest_gtfs():
        raise FileNotFoundError(
            "GTFS no encontrado"
        )

    monkeypatch.setattr(
        transform_gtfs,
        "get_latest_gtfs",
        mock_get_latest_gtfs,
    )

    with pytest.raises(
        FileNotFoundError,
        match="GTFS no encontrado",
    ):
        transform_gtfs.main()


def test_main_propagates_value_error(
    monkeypatch,
):
    dataframes = create_minimal_gtfs_data()

    monkeypatch.setattr(
        transform_gtfs,
        "get_latest_gtfs",
        lambda: Path(
            "/tmp/2026-09-11/extracted"
        ),
    )

    monkeypatch.setattr(
        transform_gtfs,
        "load_gtfs",
        lambda path: dataframes,
    )

    def mock_transform(data):
        raise ValueError(
            "Error de transformación"
        )

    monkeypatch.setattr(
        transform_gtfs,
        "transform_gtfs",
        mock_transform,
    )

    with pytest.raises(
        ValueError,
        match="Error de transformación",
    ):
        transform_gtfs.main()


def test_main_propagates_key_error(
    monkeypatch,
):
    dataframes = create_minimal_gtfs_data()

    monkeypatch.setattr(
        transform_gtfs,
        "get_latest_gtfs",
        lambda: Path(
            "/tmp/2026-09-11/extracted"
        ),
    )

    monkeypatch.setattr(
        transform_gtfs,
        "load_gtfs",
        lambda path: dataframes,
    )

    def mock_transform(data):
        raise KeyError("stops")

    monkeypatch.setattr(
        transform_gtfs,
        "transform_gtfs",
        mock_transform,
    )

    with pytest.raises(
        KeyError,
        match="stops",
    ):
        transform_gtfs.main()
