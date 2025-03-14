from prometheus_client import Gauge


_percentiles = [50, 90, 99]


def generate_metrics_for_rpc(rpc):
    return [(f"{rpc}_us_{percentile}p", f"{rpc} latency in microseconds, {percentile}th percentile") for percentile in _percentiles]


_append_deltas_metrics = generate_metrics_for_rpc("AppendDeltasRpc")

_ha_data_instances_metrics = _append_deltas_metrics


PrometheusHADataInstancesMetrics = {name: Gauge(name, description, ["instance_name"]) for name, description in _ha_data_instances_metrics}
