from prometheus_client import Gauge

_data = [
    (
        "QueryExecutionLatency_us_99p",
        "Query execution latency in microseconds, 99th percentile",
    ),
    (
        "QueryExecutionLatency_us_90p",
        "Query execution latency in microseconds, 90th percentile",
    ),
    (
        "QueryExecutionLatency_us_50p",
        "Query execution latency in microseconds, 50th percentile",
    ),
]


PrometheusQueryData = {name: Gauge(name, description, ["instance_name"]) for name, description in _data}
