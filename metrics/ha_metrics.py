_percentiles = [50, 90, 99]


def generate_timer_metrics(metric):
    return [
        (
            f"{metric}_us_{percentile}p",
            f"{metric} latency in microseconds, {percentile}th percentile",
        )
        for percentile in _percentiles
    ]


ha_data_instances_metrics = (
    generate_timer_metrics("AppendDeltasRpc")
    + generate_timer_metrics("CurrentWalRpc")
    + generate_timer_metrics("WalFilesRpc")
    + generate_timer_metrics("SnapshotRpc")
    + generate_timer_metrics("FrequentHeartbeatRpc")
    + generate_timer_metrics("HeartbeatRpc")
    + generate_timer_metrics("ReplicaStream")
    + generate_timer_metrics("SystemRecoveryRpc")
)


# Metrics specific to each coordinators
ha_coordinator_metrics = (
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


# Common metrics for all coordinators
ha_coordinators_agg_metrics = [
    ("BecomeLeaderSuccess", "How many times coordinators successfully became leaders"),
    ("FailedToBecomeLeader", "How many times coordinator failed to become leader"),
    ("SuccessfulFailovers", "How many times the failover was done successfully"),
    (
        "RaftFailedFailovers",
        "How many times failover failed because writing to Raft failed",
    ),
    (
        "NoAliveInstanceFailedFailovers",
        "How many times failover failed because no instance was alive",
    ),
    ("ShowInstance", "How many times SHOW INSTANCE query was called"),
    ("ShowInstances", "How many times SHOW INSTANCES query was called"),
    ("DemoteInstance", "How many times the user manually demoted instance"),
    (
        "UnregisterReplInstance",
        "How many times the user tried to unregister replication instance",
    ),
    (
        "RemoveCoordInstance",
        "How many times the user tried to remove coordinator instance",
    ),
    (
        "StateCheckRpcFail",
        "How many times coordinators received unsuccessful or no response to StateCheckRpc",
    ),
    (
        "StateCheckRpcSuccess",
        "How many times we received successful response to StateCheckRpc",
    ),
    (
        "UnregisterReplicaRpcFail",
        "How many times we received unsuccessful or no response to UnregisterReplicaRpc",
    ),
    (
        "UnregisterReplicaRpcSuccess",
        "How many times we received sucessful response to UnregisterReplicaRpc",
    ),
    (
        "EnableWritingOnMainRpcFail",
        "How many times we received unsuccessful or no response to EnableWritingOnMainRpc",
    ),
    (
        "EnableWritingOnMainRpcSuccess",
        "How many times we received sucessful response to EnableWritingOnMainRpc",
    ),
    (
        "PromoteToMainRpcFail",
        "How many times we received unsuccessful or no response to PromoteToMainRpc",
    ),
    (
        "PromoteToMainRpcSuccess",
        "How many times we received sucessful response to PromoteToMainRpc",
    ),
    (
        "DemoteMainToReplicaRpcFail",
        "How many times we received unsuccessful or no response to DemoteMainToReplicaRpc",
    ),
    (
        "DemoteMainToReplicaRpcSuccess",
        "How many times we received sucessful response to DemoteMainToReplicaRpc",
    ),
    (
        "RegisterReplicaOnMainRpcFail",
        "How many times we received unsuccessful or no response to RegisterReplicaOnMainRpc",
    ),
    (
        "RegisterReplicaOnMainRpcSuccess",
        "How many times we received sucessful response to RegisterReplicaOnMainRpc",
    ),
    (
        "SwapMainUUIDRpcFail",
        "How many times we received unsuccessful or no response to SwapMainUUIDRpc",
    ),
    (
        "SwapMainUUIDRpcSuccess",
        "How many times we received sucessful response to SwapMainUUIDRpc",
    ),
    (
        "GetDatabaseHistoriesRpcFail",
        "How many times we received unsuccessful or no response to GetDatabaseHistoriesRpc",
    ),
    (
        "GetDatabaseHistoriesRpcSuccess",
        "How many times we received sucessful response to GetDatabaseHistoriesRpc",
    ),
]
