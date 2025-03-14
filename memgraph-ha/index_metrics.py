from prometheus_client import Gauge

_data = [
    ("ActiveLabelIndices", "Number of active label indices in the system."),
    ("ActiveLabelPropertyIndices", "Number of active label indices in the system."),
    ("ActivePointIndices", "Number of active point indices in the system."),
    ("ActiveTextIndices", "Number of active text indices in the system."),
]


PrometheusIndexData = {name: Gauge(name, description, ["instance_name"]) for name, description in _data}
