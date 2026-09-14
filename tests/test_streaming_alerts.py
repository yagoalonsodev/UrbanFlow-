from streaming.alerts import build_arrival_alert


def event_with_wait(seconds):
    return {
        "timestamp": 1789387200,
        "destination": "Centre",
        "line": "H12",
        "route_id": "2.12.123",
        "stop": "1234",
        "time_in_minutes": seconds // 60,
        "time_in_seconds": seconds,
        "text_ca": f"{seconds} segons",
    }


def test_build_arrival_alert_returns_none_below_threshold():
    assert build_arrival_alert(event_with_wait(600)) is None


def test_build_arrival_alert_creates_critical_alert_above_threshold():
    alert = build_arrival_alert(event_with_wait(601))

    assert alert["alert_type"] == "critical_arrival_wait"
    assert alert["severity"] == "critical"
    assert alert["route_id"] == "2.12.123"
    assert alert["time_in_seconds"] == 601