from prometheus_client import Gauge

_data = [
    ("MessagesConsumed", "Number of consumed streamed messages."),
    ("StreamsCreated", "Number of Streams created."),
]


PrometheusStreamData = {name: Gauge(name, description, ["instance_name"]) for name, description in _data}
