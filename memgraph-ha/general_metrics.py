from prometheus_client import Gauge

_data = [
    ("average_degree", "Average node degree."),
    ("disk_usage", "Amount of disk usage."),
    ("edge_count", "Edge count."),
    ("memory_usage", "Amount of memory usage."),
    ("peak_memory_usage", "Peak memory usage."),
    ("unreleased_delta_objects", "Number of unreleased delta objects."),
    ("vertex_count", "Vertex count."),
    ("SocketConnect_us_50p", "Latency of connecting to the socket, 50th percentile."),
    ("SocketConnect_us_90p", "Latency of connecting to the socket, 90th percentile."),
    ("SocketConnect_us_99p", "Latency of connecting to the socket, 99th percentile.")
]

# General metrics specific to each instance
PrometheusGeneralData = {name: Gauge(name, description, ["instance_name"]) for name, description in _data}
