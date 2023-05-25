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
    Transaction = "Transaction"
    Trigger = "Trigger"
    General = "General"


INDEX = {
    "ActiveLabelIndices": Gauge(
        "ActiveLabelIndices", "Number of active label indices in the system."
    ),
    "ActiveLabelPropertyIndices": Gauge(
        "ActiveLabelPropertyIndices",
        "Number of active label indices in the system.",
    ),
}

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
    "LimitOperator",
    "MergeOperator",
    "OnceOperator",
    "OptionalOperator",
    "OrderByOperator",
    "ProduceOperator",
    "RemoveLabelsOperator",
    "RemovePropertyOperator",
    "ScanAllByIdOperator",
    "ScanAllByLabelOperator",
    "ScanAllByLabelPropertyOperator",
    "ScanAllByLabelPropertyRangeOperator",
    "ScanAllByLabelPropertyValueOperator",
    "ScanAllOperator",
    "SetLabelsOperator",
    "SetPropertiesOperator",
    "SetPropertyOperator",
    "SkipOperator",
    "UnionOperator",
    "UnwindOperator",
]

OPERATOR = {
    name: Gauge(name, f"Number of times {name} has been called.")
    for name in operator_names
}


QUERY = {
    "QueryExecutionLatency_us_99p": Gauge(
        "QueryExecutionLatency_us_99p",
        "Query execution latency in microseconds, 99th percentile",
    ),
    "QueryExecutionLatency_us_90p": Gauge(
        "QueryExecutionLatency_us_90p",
        "Query execution latency in microseconds, 90th percentile",
    ),
    "QueryExecutionLatency_us_50p": Gauge(
        "QueryExecutionLatency_us_50p",
        "Query execution latency in microseconds, 50th percentile",
    ),
}

QUERY_TYPE = {
    "ReadQuery": Gauge("ReadQuery", "Number of read-only queries executed."),
    "ReadWriteQuery": Gauge("ReadWriteQuery", "Number of write-only queries executed."),
    "WriteQuery": Gauge("WriteQuery", "Number of read-write queries executed."),
}

SESSION = {
    "ActiveBoltSessions": Gauge(
        "ActiveBoltSessions", "Number of active Bolt connections."
    ),
    "ActiveSSLSessions": Gauge(
        "ActiveSSLSessions", "Number of active SSL connections."
    ),
    "ActiveSessions": Gauge("ActiveSessions", "Number of active connections."),
    "ActiveTCPSessions": Gauge(
        "ActiveTCPSessions", "Number of active TCP connections."
    ),
    "ActiveWebSocketSessions": Gauge(
        "ActiveWebSocketSessions", "Number of active websocket connections."
    ),
    "BoltMessages": Gauge("BoltMessages", "Number of Bolt messages sent."),
}

SNAPSHOT = {
    "SnapshotCreationLatency_us_99p": Gauge(
        "SnapshotCreationLatency_us_99p",
        "Snapshot creation latency in microseconds, 99th percentile",
    ),
    "SnapshotCreationLatency_us_90p": Gauge(
        "SnapshotCreationLatency_us_90p",
        "Snapshot creation latency in microseconds, 90th percentile",
    ),
    "SnapshotCreationLatency_us_50p": Gauge(
        "SnapshotCreationLatency_us_50p",
        "Snapshot creation latency in microseconds, 50th percentile",
    ),
    "SnapshotRecoveryLatency_us_99p": Gauge(
        "SnapshotRecoveryLatency_us_99p",
        "Snapshot creation latency in microseconds, 99th percentile",
    ),
    "SnapshotRecoveryLatency_us_90p": Gauge(
        "SnapshotRecoveryLatency_us_90p",
        "Snapshot creation latency in microseconds, 90th percentile",
    ),
    "SnapshotRecoveryLatency_us_50p": Gauge(
        "SnapshotRecoveryLatency_us_50p",
        "Snapshot creation latency in microseconds, 50th percentile",
    ),
}

STREAM = {
    "MessagesConsumed": Gauge(
        "MessagesConsumed", "Number of consumed streamed messages."
    ),
    "StreamsCreated": Gauge("StreamsCreated", "Number of Streams created."),
}

TRANSACTION = {
    "ActiveTransactions": Gauge("ActiveTransactions", "Number of active transactions."),
    "CommitedTransactions": Gauge(
        "CommitedTransactions", "Number of committed transactions."
    ),
    "FailedQuery": Gauge("FailedQuery", "Number of times executing a query failed."),
    "RollbackedTransactions": Gauge(
        "RollbackedTransactions", "Number of rollbacked transactions."
    ),
}

TRIGGER = {
    "TriggersCreated": Gauge("TriggersCreated", "Number of Triggers created."),
    "TriggersExecuted": Gauge("TriggersExecuted", "Number of Triggers executed."),
}

GENERAL = {
    "average_degree": Gauge("average_degree", "Average node degree."),
    "disk_usage": Gauge("disk_usage", "Amount of disk usage."),
    "edge_count": Gauge("edge_count", "Edge count."),
    "memory_usage": Gauge("memory_usage", "Amount of memory usage."),
    "vertex_count": Gauge("vertex_count", "Vertex count."),
}


def update_metrics(data: Dict[str, Dict[str, int]]):
    for key, value in data[DataCategoryConstants.Index].items():
        INDEX[key].set(value)
    for key, value in data[DataCategoryConstants.Operator].items():
        OPERATOR[key].set(value)
    for key, value in data[DataCategoryConstants.Query].items():
        QUERY[key].set(value)
    for key, value in data[DataCategoryConstants.QueryType].items():
        QUERY_TYPE[key].set(value)
    for key, value in data[DataCategoryConstants.Session].items():
        SESSION[key].set(value)
    for key, value in data[DataCategoryConstants.Snapshot].items():
        SNAPSHOT[key].set(value)
    for key, value in data[DataCategoryConstants.Stream].items():
        STREAM[key].set(value)
    for key, value in data[DataCategoryConstants.Transaction].items():
        TRANSACTION[key].set(value)
    for key, value in data[DataCategoryConstants.Trigger].items():
        TRIGGER[key].set(value)
    for key, value in data[DataCategoryConstants.General].items():
        GENERAL[key].set(value)
