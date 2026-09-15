import pytest

from agent.guardrails import validate_read_only_sql


def test_guardrail_adds_limit_to_select():
    assert validate_read_only_sql("SELECT * FROM trips") == "SELECT * FROM trips LIMIT 2000"


@pytest.mark.parametrize(
    "query",
    [
        "DELETE FROM trips",
        "SELECT * FROM trips; DROP TABLE trips",
        "UPDATE trips SET trip_id = 'x'",
        "WITH trips_cte AS (SELECT * FROM trips) SELECT * FROM trips_cte",
        "EXPLAIN SELECT * FROM trips",
    ],
)
def test_guardrail_rejects_unsafe_sql(query):
    with pytest.raises(ValueError):
        validate_read_only_sql(query)


def test_guardrail_allows_only_select():
    assert validate_read_only_sql("SELECT trip_id FROM trips") == (
        "SELECT trip_id FROM trips LIMIT 2000"
    )