from prometheus_client import Gauge

_data = [
    ("TriggersCreated", "Number of Triggers created."),
    ("TriggersExecuted", "Number of Triggers executed."),
]


PrometheusTriggerData = {name: Gauge(name, description, ["instance_name"]) for name, description in _data}
