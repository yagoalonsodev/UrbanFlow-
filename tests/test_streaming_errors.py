from streaming.errors import build_validation_error_event


def test_build_validation_error_event_preserves_invalid_event():
    event = {"route_id": None, "stop": "1234"}

    result = build_validation_error_event(event, "route_id obligatorio")

    assert result["error_type"] == "validation_error"
    assert result["error_message"] == "route_id obligatorio"
    assert result["event"] == event
    assert isinstance(result["timestamp"], int)


def test_build_validation_error_event_preserves_timestamp():
    event = {"timestamp": 1789387200, "route_id": None}

    result = build_validation_error_event(event, "evento inválido")

    assert result["timestamp"] == 1789387200