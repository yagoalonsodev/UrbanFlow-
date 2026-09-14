import pytest

from streaming.event_validation import validate_realtime_event


def valid_event():
    return {
        "timestamp": 1789387200,
        "destination": "Centre",
        "line": "H12",
        "route_id": "2.12.123",
        "stop": "1234",
        "time_in_minutes": 4,
        "time_in_seconds": 240,
        "text_ca": "4 min",
    }


def test_validate_realtime_event_accepts_valid_event():
    event = valid_event()

    assert validate_realtime_event(event) is event


@pytest.mark.parametrize(
    "field",
    ["timestamp", "line", "route_id", "stop", "time_in_minutes", "time_in_seconds"],
)
def test_validate_realtime_event_rejects_missing_required_field(field):
    event = valid_event()
    event[field] = None

    with pytest.raises(ValueError, match="campos obligatorios"):
        validate_realtime_event(event)


def test_validate_realtime_event_rejects_negative_time():
    event = valid_event()
    event["time_in_seconds"] = -1

    with pytest.raises(ValueError, match="no puede ser negativo"):
        validate_realtime_event(event)


def test_validate_realtime_event_rejects_unexpected_field():
    event = valid_event()
    event["unknown"] = "value"

    with pytest.raises(ValueError, match="campos no esperados"):
        validate_realtime_event(event)