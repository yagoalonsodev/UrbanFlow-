from numbers import Integral


EXPECTED_FIELDS = {
    "timestamp",
    "destination",
    "line",
    "route_id",
    "stop",
    "time_in_minutes",
    "time_in_seconds",
    "text_ca",
}

REQUIRED_FIELDS = {
    "timestamp",
    "line",
    "route_id",
    "stop",
    "time_in_minutes",
    "time_in_seconds",
}


def validate_realtime_event(event: dict) -> dict:
    """Valida un mensaje normalizado antes de enviarlo a Kafka."""

    if not isinstance(event, dict):
        raise ValueError("El evento GTFS-RT debe ser un objeto JSON.")

    unexpected_fields = set(event) - EXPECTED_FIELDS
    if unexpected_fields:
        raise ValueError(
            f"El evento GTFS-RT contiene campos no esperados: {unexpected_fields}"
        )

    missing_fields = {
        field
        for field in REQUIRED_FIELDS
        if field not in event or event[field] is None
    }
    if missing_fields:
        raise ValueError(
            f"El evento GTFS-RT no contiene campos obligatorios: {missing_fields}"
        )

    for field in ("line", "route_id", "stop"):
        if not isinstance(event[field], str) or not event[field].strip():
            raise ValueError(f"El campo {field} no puede estar vacío.")

    if not isinstance(event["timestamp"], Integral) or event["timestamp"] <= 0:
        raise ValueError("El timestamp del evento GTFS-RT no es válido.")

    for field in ("time_in_minutes", "time_in_seconds"):
        if isinstance(event[field], bool) or not isinstance(event[field], Integral):
            raise ValueError(f"El campo {field} debe ser un entero.")
        if event[field] < 0:
            raise ValueError(f"El campo {field} no puede ser negativo.")

    return event