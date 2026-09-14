import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType, StructField, StructType

from processing.data_quality import (
    check_coordinates,
    check_null_identifiers,
    check_referential_integrity,
)


@pytest.fixture(scope="module")
def spark():
    session = (
        SparkSession.builder
        .master("local[2]")
        .appName("urbanflow-data-quality-tests")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    yield session
    session.stop()


def valid_dataframes(spark):
    return {
        "routes": spark.createDataFrame([("R1",)], ["route_id"]),
        "trips": spark.createDataFrame([("T1", "R1")], ["trip_id", "route_id"]),
        "stops": spark.createDataFrame([("S1", 41.38, 2.17)], ["stop_id", "stop_lat", "stop_lon"]),
        "stop_times": spark.createDataFrame([("T1", "S1")], ["trip_id", "stop_id"]),
        "calendar": spark.createDataFrame([("C1",)], ["service_id"]),
    }


def test_quality_checks_accept_valid_data(spark):
    dataframes = valid_dataframes(spark)

    check_null_identifiers(dataframes)
    check_referential_integrity(dataframes)
    check_coordinates(dataframes)


def test_quality_checks_reject_null_identifier(spark):
    dataframes = valid_dataframes(spark)
    dataframes["routes"] = spark.createDataFrame(
        [(None,)],
        StructType([StructField("route_id", StringType(), True)]),
    )

    with pytest.raises(ValueError, match="identificadores nulos"):
        check_null_identifiers(dataframes)


def test_quality_checks_reject_invalid_reference(spark):
    dataframes = valid_dataframes(spark)
    dataframes["trips"] = spark.createDataFrame([("T1", "R2")], ["trip_id", "route_id"])

    with pytest.raises(ValueError, match="no tienen correspondencia"):
        check_referential_integrity(dataframes)


def test_quality_checks_reject_invalid_coordinates(spark):
    dataframes = valid_dataframes(spark)
    dataframes["stops"] = spark.createDataFrame([("S1", 95.0, 2.17)], ["stop_id", "stop_lat", "stop_lon"])

    with pytest.raises(ValueError, match="coordenadas"):
        check_coordinates(dataframes)