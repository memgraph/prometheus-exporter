from prometheus_client import Gauge

_data = [
    ("ReadQuery", "Number of read-only queries executed."),
    ("ReadWriteQuery", "Number of write-only queries executed."),
    ("WriteQuery", "Number of read-write queries executed."),
]

PrometheusQueryTypeData = {name: Gauge(name, description, ["instance_name"]) for name, description in _data}
