from typing import Dict

from prometheus_client import Gauge


class DataCategoryConstants:
    Index = "Index"
    Operator = "Operator"
    Query = "Query"
    QueryType = "QueryType"
    Session = "Session"
    Snapshot = "Snapshot"
    Stream = "Stream"
    TTL = "TTL"
    Transaction = "Transaction"
    Trigger = "Trigger"
    General = "General"


index_data = [
    ("ActiveLabelIndices", "Number of active label indices in the system."),
    ("ActiveLabelPropertyIndices", "Number of active label indices in the system."),
    ("ActivePointIndices", "Number of active point indices in the system."),
    ("ActiveTextIndices", "Number of active text indices in the system."),
]

operator_names = [
    "AccumulateOperator",
    "AggregateOperator",
    "ApplyOperator",
    "CallProcedureOperator",
    "CartesianOperator",
    "ConstructNamedPathOperator",
    "CreateExpandOperator",
    "CreateNodeOperator",
    "DeleteOperator",
    "DistinctOperator",
    "EdgeUniquenessFilterOperator",
    "EmptyResultOperator",
    "EvaluatePatternFilterOperator",
    "ExpandOperator",
    "ExpandVariableOperator",
    "FilterOperator",
    "ForeachOperator",
    "HashJoinOperator",
    "IndexedJoinOperator",
    "LimitOperator",
    "MergeOperator",
    "OnceOperator",
    "OptionalOperator",
    "OrderByOperator",
    "PeriodicCommitOperator",
    "PeriodicSubqueryOperator",
    "ProduceOperator",
    "RemoveLabelsOperator",
    "RemovePropertyOperator",
    "RollUpApplyOperator",
    "ScanAllByEdgeIdOperator",
    "ScanAllByEdgeOperator",
    "ScanAllByEdgeTypeOperator",
    "ScanAllByEdgeTypePropertyOperator",
    "ScanAllByEdgeTypePropertyRangeOperator",
    "ScanAllByEdgeTypePropertyValueOperator",
    "ScanAllByIdOperator",
    "ScanAllByLabelOperator",
    "ScanAllByLabelPropertyOperator",
    "ScanAllByLabelPropertyRangeOperator",
    "ScanAllByLabelPropertyValueOperator",
    "ScanAllByPointDistanceOperator",
    "ScanAllByPointWithinbboxOperator",
    "ScanAllOperator",
    "SetLabelsOperator",
    "SetPropertiesOperator",
    "SetPropertyOperator",
    "SkipOperator",
    "UnionOperator",
    "UnwindOperator",
]

query_data = [
    (
        "QueryExecutionLatency_us_99p",
        "Query execution latency in microseconds, 99th percentile",
    ),
    (
        "QueryExecutionLatency_us_90p",
        "Query execution latency in microseconds, 90th percentile",
    ),
    (
        "QueryExecutionLatency_us_50p",
        "Query execution latency in microseconds, 50th percentile",
    ),
]

query_type_data = [
    ("ReadQuery", "Number of read-only queries executed."),
    ("ReadWriteQuery", "Number of write-only queries executed."),
    ("WriteQuery", "Number of read-write queries executed."),
]

session_data = [
    ("ActiveBoltSessions", "Number of active Bolt connections."),
    ("ActiveSSLSessions", "Number of active SSL connections."),
    ("ActiveSessions", "Number of active connections."),
    ("ActiveTCPSessions", "Number of active TCP connections."),
    ("ActiveWebSocketSessions", "Number of active websocket connections."),
    ("BoltMessages", "Number of Bolt messages sent."),
]

snapshot_data = [
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

stream_data = [
    ("MessagesConsumed", "Number of consumed streamed messages."),
    ("StreamsCreated", "Number of Streams created."),
]

TTL = [
    ("DeletedEdges", "Number of deleted TTL edges."),
    ("DeletedNodes", "Number of deleted TTL nodes."),
]

transaction_data = [
    ("ActiveTransactions", "Number of active transactions."),
    ("CommitedTransactions", "Number of committed transactions."),
    ("FailedPrepare", "Number of failed prepare queries."),
    ("FailedPull", "Number of failed pulls."),
    ("FailedQuery", "Number of times executing a query failed."),
    ("RollbackedTransactions", "Number of rollbacked transactions."),
    ("SuccessfulQuery", "Number of successful queries"),
]

trigger_data = [
    ("TriggersCreated", "Number of Triggers created."),
    ("TriggersExecuted", "Number of Triggers executed."),
]

general_data = [
    ("average_degree", "Average node degree."),
    ("disk_usage", "Amount of disk usage."),
    ("edge_count", "Edge count."),
    ("memory_usage", "Amount of memory usage."),
    ("peak_memory_usage", "Peak memory usage."),
    ("unreleased_delta_objects", "Number of unreleased delta objects."),
    ("vertex_count", "Vertex count."),
]

INDEX = {name: Gauge(name, description) for name, description in index_data}
OPERATOR = {
    name: Gauge(name, f"Number of times {name} has been called.")
    for name in operator_names
}
QUERY = {name: Gauge(name, description) for name, description in query_data}
QUERY_TYPE = {name: Gauge(name, description) for name, description in query_type_data}
SESSION = {name: Gauge(name, description) for name, description in session_data}
SNAPSHOT = {name: Gauge(name, description) for name, description in snapshot_data}
STREAM = {name: Gauge(name, description) for name, description in stream_data}
TRANSACTION = {name: Gauge(name, description) for name, description in transaction_data}
TRIGGER = {name: Gauge(name, description) for name, description in trigger_data}
GENERAL = {name: Gauge(name, description) for name, description in general_data}


def update_prom_metrics(mg_data, prom_data):
    for key, value in mg_data.items():
        if key not in prom_data:
            continue
        prom_data[key].set(value)


def update_metrics(mg_data: Dict[str, Dict[str, int]]):
    update_prom_metrics(mg_data[DataCategoryConstants.Index], INDEX)
    update_prom_metrics(mg_data[DataCategoryConstants.Operator], OPERATOR)
    update_prom_metrics(mg_data[DataCategoryConstants.Query], QUERY)
    update_prom_metrics(mg_data[DataCategoryConstants.QueryType], QUERY_TYPE)
    update_prom_metrics(mg_data[DataCategoryConstants.Session], SESSION)
    update_prom_metrics(mg_data[DataCategoryConstants.Snapshot], SNAPSHOT)
    update_prom_metrics(mg_data[DataCategoryConstants.Stream], STREAM)
    update_prom_metrics(mg_data[DataCategoryConstants.Transaction], TRANSACTION)
    update_prom_metrics(mg_data[DataCategoryConstants.Trigger], TRIGGER)
    update_prom_metrics(mg_data[DataCategoryConstants.General], GENERAL)
