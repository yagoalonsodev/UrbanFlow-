ALERT_THRESHOLD_SECONDS = 600


def build_arrival_alert(event: dict) -> dict | None:
    """Construye una alerta cuando la espera de llegada supera diez minutos."""

    if event["time_in_seconds"] <= ALERT_THRESHOLD_SECONDS:
        return None

    return {
        "timestamp": event["timestamp"],
        "alert_type": "critical_arrival_wait",
        "severity": "critical",
        "line": event["line"],
        "route_id": event["route_id"],
        "stop": event["stop"],
        "time_in_seconds": event["time_in_seconds"],
        "destination": event.get("destination"),
        "message": (
            "La espera estimada de llegada supera "
            f"{ALERT_THRESHOLD_SECONDS} segundos."
        ),
    }