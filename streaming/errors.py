import time


def build_validation_error_event(event: dict, error: str) -> dict:
    """Construye el evento que se publica en transport-errors."""

    return {
        "timestamp": event.get("timestamp", int(time.time())),
        "error_type": "validation_error",
        "error_message": error,
        "event": event,
    }