from prometheus_client import Gauge

_data = [
    ("ActiveBoltSessions", "Number of active Bolt connections."),
    ("ActiveSSLSessions", "Number of active SSL connections."),
    ("ActiveSessions", "Number of active connections."),
    ("ActiveTCPSessions", "Number of active TCP connections."),
    ("ActiveWebSocketSessions", "Number of active websocket connections."),
    ("BoltMessages", "Number of Bolt messages sent."),
]


PrometheusSessionData = {name: Gauge(name, description, ["instance_name"]) for name, description in _data}
