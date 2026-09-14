import pandas as pd
import pytest

from processing.validate_processed_snapshot import validate_processed_dataframes


def valid_dataframes():
    return {
        "agency": pd.DataFrame({"agency_name": ["TMB"]}),
        "routes": pd.DataFrame({"route_id": ["R1"]}),
        "stops": pd.DataFrame({"stop_id": ["S1"]}),
        "calendar": pd.DataFrame({"service_id": ["C1"]}),
        "calendar_dates": pd.DataFrame({"service_id": ["C1"], "date": ["20260914"]}),
        "trips": pd.DataFrame({"trip_id": ["T1"], "route_id": ["R1"], "service_id": ["C1"]}),
        "stop_times": pd.DataFrame({"trip_id": ["T1"], "stop_id": ["S1"], "stop_sequence": [1]}),
    }


def test_validate_processed_dataframes_accepts_valid_data():
    counts = validate_processed_dataframes(valid_dataframes())

    assert counts["trips"] == 1
    assert counts["stop_times"] == 1


def test_validate_processed_dataframes_rejects_missing_column():
    dataframes = valid_dataframes()
    dataframes["trips"] = dataframes["trips"].drop(columns=["service_id"])

    with pytest.raises(ValueError, match="columnas obligatorias"):
        validate_processed_dataframes(dataframes)


def test_validate_processed_dataframes_rejects_invalid_reference():
    dataframes = valid_dataframes()
    dataframes["stop_times"].loc[0, "trip_id"] = "T2"

    with pytest.raises(ValueError, match="trip_id sin correspondencia"):
        validate_processed_dataframes(dataframes)


def test_validate_processed_dataframes_rejects_duplicate_key():
    dataframes = valid_dataframes()
    dataframes["trips"] = pd.concat(
        [dataframes["trips"], dataframes["trips"]],
        ignore_index=True,
    )

    with pytest.raises(ValueError, match="claves duplicadas"):
        validate_processed_dataframes(dataframes)