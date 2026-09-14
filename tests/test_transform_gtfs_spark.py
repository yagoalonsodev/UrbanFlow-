import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StringType,
    StructField,
    StructType,
)

from processing import transform_gtfs_spark


@pytest.fixture(scope="module")
def spark():
    session = (
        SparkSession.builder
        .master("local[2]")
        .appName("urbanflow-transform-tests")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    yield session
    session.stop()


def test_transform_routes_removes_duplicates_trims_and_casts(spark):
    dataframe = spark.createDataFrame(
        [(" R1 ", " L1 ", " Ruta 1 ", "3"), (" R1 ", " L1 ", " Ruta 1 ", "3")],
        ["route_id", "route_short_name", "route_long_name", "route_type"],
    )

    result = transform_gtfs_spark.transform_routes(dataframe)
    row = result.first()

    assert result.count() == 1
    assert row.route_id == " R1 "
    assert row.route_short_name == "L1"
    assert row.route_long_name == "Ruta 1"
    assert row.route_type == 3


def test_transform_trips_casts_identifiers_and_trims_headsign(spark):
    dataframe = spark.createDataFrame(
        [(" T1 ", " R1 ", " S1 ", " Centro ", "1")],
        ["trip_id", "route_id", "service_id", "trip_headsign", "direction_id"],
    )

    row = transform_gtfs_spark.transform_trips(dataframe).first()

    assert row.trip_id == " T1 "
    assert row.route_id == " R1 "
    assert row.service_id == " S1 "
    assert row.trip_headsign == "Centro"
    assert row.direction_id == 1


def test_transform_stops_removes_null_coordinates_and_casts_values(spark):
    schema = StructType([
        StructField("stop_id", StringType(), True),
        StructField("stop_code", StringType(), True),
        StructField("stop_name", StringType(), True),
        StructField("stop_lat", StringType(), True),
        StructField("stop_lon", StringType(), True),
    ])
    dataframe = spark.createDataFrame(
        [("S1", "001", " Centro ", "41.38", "2.17"), ("S2", "002", "Sin coordenadas", None, "2.18")],
        schema,
    )

    result = transform_gtfs_spark.transform_stops(dataframe)
    row = result.first()

    assert result.count() == 1
    assert row.stop_name == "Centro"
    assert row.stop_lat == pytest.approx(41.38)
    assert row.stop_lon == pytest.approx(2.17)


def test_transform_stop_times_casts_sequence_trims_times_and_removes_null_ids(spark):
    schema = StructType([
        StructField("trip_id", StringType(), True),
        StructField("stop_id", StringType(), True),
        StructField("stop_sequence", StringType(), True),
        StructField("arrival_time", StringType(), True),
        StructField("departure_time", StringType(), True),
    ])
    dataframe = spark.createDataFrame(
        [("T1", "S1", "1", " 08:00:00 ", " 08:00:30 "), (None, "S2", "2", "09:00:00", "09:00:00")],
        schema,
    )

    row = transform_gtfs_spark.transform_stop_times(dataframe).first()

    assert row.trip_id == "T1"
    assert row.stop_id == "S1"
    assert row.stop_sequence == 1
    assert row.arrival_time == "08:00:00"
    assert row.departure_time == "08:00:30"


def test_transform_calendar_converts_dates(spark):
    dataframe = spark.createDataFrame(
        [("S1", "1", "20260101", "20261231")],
        ["service_id", "monday", "start_date", "end_date"],
    )

    row = transform_gtfs_spark.transform_calendar(dataframe).first()

    assert row.service_id == "S1"
    assert str(row.start_date) == "2026-01-01"
    assert str(row.end_date) == "2026-12-31"


def test_transform_calendar_dates_casts_date_and_exception(spark):
    dataframe = spark.createDataFrame(
        [("S1", "20260914", "2")],
        ["service_id", "date", "exception_type"],
    )

    row = transform_gtfs_spark.transform_calendar_dates(dataframe).first()

    assert row.service_id == "S1"
    assert str(row.date) == "2026-09-14"
    assert row.exception_type == 2