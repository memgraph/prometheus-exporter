from prometheus_client import Gauge


_percentiles = [50, 90, 99]


def generate_timer_metrics(metric):
    return [
        (
            f"{metric}_us_{percentile}p",
            f"{metric} latency in microseconds, {percentile}th percentile",
        )
        for percentile in _percentiles
    ]


_ha_data_instances_metrics = (
    generate_timer_metrics("AppendDeltasRpc")
    + generate_timer_metrics("CurrentWalRpc")
    + generate_timer_metrics("SnapshotRpc")
    + generate_timer_metrics("FrequentHeartbeatRpc")
    + generate_timer_metrics("HeartbeatRpc")
    + generate_timer_metrics("ReplicaStream")
    + generate_timer_metrics("SystemRecoveryRpc")
)
# Metrics related to HA specific to each data instance
PrometheusHADataInstancesMetrics = {
    name: Gauge(name, description, ["instance_name"])
    for name, description in _ha_data_instances_metrics
}


# Metrics specific to each coordinators
_ha_coordinator_metrics = (
    generate_timer_metrics("ChooseMostUpToDateInstance")
    + generate_timer_metrics("DemoteMainToReplicaRpc")
    + generate_timer_metrics("EnableWritingOnMainRpc")
    + generate_timer_metrics("GetDatabaseHistoriesRpc")
    + generate_timer_metrics("GetHistories")
    + generate_timer_metrics("InstanceFailCallback")
    + generate_timer_metrics("InstanceSuccCallback")
    + generate_timer_metrics("PromoteToMainRpc")
    + generate_timer_metrics("RegisterReplicaOnMainRpc")
    + generate_timer_metrics("StateCheckRpc")
    + generate_timer_metrics("UnregisterReplicaRpc")
)

# Metrics specific to each coordinator
PrometheusHACoordinatorMetrics = {
    name: Gauge(name, description, ["instance_name"])
    for name, description in _ha_coordinator_metrics
}


# Common metrics for all coordinators
_ha_coordinators_agg_metrics = [
    ("BecomeLeaderSuccess", "How many times coordinators successfully became leaders")
]

# Metrics common to all coordinators
PrometheusHACoordinatorsAggMetrics = {
    name: Gauge(name, description) for name, description in _ha_coordinators_agg_metrics
}
