from prometheus_client import Gauge

_data = [
    ("average_degree", "Average node degree."),
    ("disk_usage", "Amount of disk usage."),
    ("edge_count", "Edge count."),
    ("memory_usage", "Amount of memory usage."),
    ("peak_memory_usage", "Peak memory usage."),
    ("unreleased_delta_objects", "Number of unreleased delta objects."),
    ("vertex_count", "Vertex count."),
]

# General metrics specific to each instance
PrometheusGeneralData = {name: Gauge(name, description, ["instance_name"]) for name, description in _data}
