import os

import pytest

import streaming.producer as producer
import streaming.spark_streaming as spark_streaming


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeKafkaProducer:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.sent = []
        self.flushed = False

    def send(self, topic, value):
        self.sent.append((topic, value))

    def flush(self):
        self.flushed = True


class FakeWrite:
    def __init__(self):
        self.options = {}
        self.saved = False

    def format(self, value):
        self.options["format"] = value
        return self

    def option(self, key, value):
        self.options[key] = value
        return self

    def mode(self, value):
        self.options["mode"] = value
        return self

    def save(self):
        self.saved = True


class FakeBatch:
    def __init__(self, empty=False, rows=0):
        self.empty = empty
        self.rows = rows
        self.write = FakeWrite()

    def isEmpty(self):
        return self.empty

    def count(self):
        return self.rows


def test_create_producer_configures_json_serializer(monkeypatch):
    captured = {}

    def fake_constructor(**kwargs):
        captured.update(kwargs)
        return FakeKafkaProducer(**kwargs)

    monkeypatch.setattr(producer, "KafkaProducer", fake_constructor)

    result = producer.create_producer()

    assert result.kwargs["bootstrap_servers"] == producer.KAFKA_BOOTSTRAP_SERVERS
    assert captured["value_serializer"]({"line": "H12"}) == b'{"line": "H12"}'


def test_get_tmb_data_sends_credentials_and_returns_json(monkeypatch):
    captured = {}

    def fake_get(url, params, timeout):
        captured.update(url=url, params=params, timeout=timeout)
        return FakeResponse({"data": {"ibus": [{"line": "H12"}]}})

    monkeypatch.setattr(producer.requests, "get", fake_get)

    result = producer.get_tmb_data()

    assert result["data"]["ibus"][0]["line"] == "H12"
    assert captured["url"] == producer.TMB_REALTIME_URL
    assert captured["params"] == {
        "app_id": producer.TMB_APP_ID,
        "app_key": producer.TMB_APP_KEY,
    }
    assert captured["timeout"] == 10


def test_write_to_postgres_skips_empty_batch():
    batch = FakeBatch(empty=True)

    spark_streaming.write_to_postgres(batch, 1)

    assert batch.write.saved is False


def test_write_to_postgres_writes_non_empty_batch(monkeypatch):
    batch = FakeBatch(rows=2)
    monkeypatch.setattr(spark_streaming, "POSTGRES_URL", "jdbc:test")
    monkeypatch.setattr(spark_streaming, "POSTGRES_USER", "user")
    monkeypatch.setattr(spark_streaming, "POSTGRES_PASSWORD", "password")
    monkeypatch.setattr(spark_streaming, "POSTGRES_TABLE", "realtime_bus_arrivals")

    spark_streaming.write_to_postgres(batch, 7)

    assert batch.write.saved is True
    assert batch.write.options == {
        "format": "jdbc",
        "url": "jdbc:test",
        "dbtable": "realtime_bus_arrivals",
        "user": "user",
        "password": "password",
        "driver": "org.postgresql.Driver",
        "mode": "append",
    }


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("KAFKA_INTEGRATION") != "1",
    reason="Requiere KAFKA_INTEGRATION=1 y conectividad con Kafka.",
)
def test_real_kafka_accepts_event():
    kafka_producer = producer.create_producer()
    try:
        future = kafka_producer.send(
            producer.KAFKA_TOPIC_GTFS_REALTIME,
            {"test": "urbanflow"},
        )
        future.get(timeout=10)
    finally:
        kafka_producer.close()