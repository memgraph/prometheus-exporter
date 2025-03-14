from prometheus_client import Gauge

_data = [
    ("DeletedEdges", "Number of deleted TTL edges."),
    ("DeletedNodes", "Number of deleted TTL nodes."),
]


PrometheusTTLData = {name: Gauge(name, description, ["instance_name"]) for name, description in _data}
