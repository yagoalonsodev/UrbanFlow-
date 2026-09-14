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
    ],
)
def test_guardrail_rejects_unsafe_sql(query):
    with pytest.raises(ValueError):
        validate_read_only_sql(query)