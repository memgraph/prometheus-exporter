from prometheus_client import Gauge

_data = [
    (
        "SnapshotCreationLatency_us_99p",
        "Snapshot creation latency in microseconds, 99th percentile.",
    ),
    (
        "SnapshotCreationLatency_us_90p",
        "Snapshot creation latency in microseconds, 90th percentile.",
    ),
    (
        "SnapshotCreationLatency_us_50p",
        "Snapshot creation latency in microseconds, 50th percentile.",
    ),
    (
        "SnapshotRecoveryLatency_us_99p",
        "Snapshot recovery latency in microseconds, 99th percentile.",
    ),
    (
        "SnapshotRecoveryLatency_us_90p",
        "Snapshot recovery latency in microseconds, 90th percentile.",
    ),
    (
        "SnapshotRecoveryLatency_us_50p",
        "Snapshot recovery latency in microseconds, 50th percentile.",
    ),
]


PrometheusSnapshotData = {name: Gauge(name, description, ["instance_name"]) for name, description in _data}
