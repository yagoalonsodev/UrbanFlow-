import json
import time

import requests
from kafka import KafkaProducer

from utils.config import TMB_APP_ID, TMB_APP_KEY
from utils.constants import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC_GTFS_REALTIME,
    STREAMING_INTERVAL_SECONDS,
    TMB_REALTIME_URL,
)


def create_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )


def get_tmb_data():
    params = {
        "app_id": TMB_APP_ID,
        "app_key": TMB_APP_KEY,
    }

    response = requests.get(
        TMB_REALTIME_URL,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def main():
    print("=" * 50)
    print("URBANFLOW - TMB → KAFKA PRODUCER")
    print("=" * 50)

    if not TMB_APP_ID or not TMB_APP_KEY:
        raise RuntimeError(
            "No se han encontrado TMB_APP_ID o TMB_APP_KEY."
        )

    producer = create_producer()

    print(f"Kafka: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Topic: {KAFKA_TOPIC_GTFS_REALTIME}")
    print(f"Intervalo: {STREAMING_INTERVAL_SECONDS} segundos")
    print()

    try:
        while True:
            try:
                data = get_tmb_data()

                ibus = data.get("data", {}).get("ibus", [])

                print(
                    f"Datos recibidos de TMB: {len(ibus)}"
                )

                messages_sent = 0

                for bus in ibus:
                    message = {
                        "timestamp": int(time.time()),
                        "destination": bus.get("destination"),
                        "line": bus.get("line"),
                        "route_id": bus.get("routeId"),
                        "stop": bus.get("stop"),
                        "time_in_minutes": bus.get("t-in-min"),
                        "time_in_seconds": bus.get("t-in-s"),
                        "text_ca": bus.get("text-ca"),
                    }

                    producer.send(
                        KAFKA_TOPIC_GTFS_REALTIME,
                        value=message,
                    )

                    messages_sent += 1

                producer.flush()

                print(
                    f"Mensajes enviados a Kafka: {messages_sent}"
                )

            except requests.RequestException as error:
                print(f"Error API TMB: {error}")

            except Exception as error:
                print(f"Error procesando datos: {error}")

            print(
                f"Esperando {STREAMING_INTERVAL_SECONDS} segundos...\n"
            )

            time.sleep(STREAMING_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nProducer detenido.")

    finally:
        producer.close()


if __name__ == "__main__":
    main()