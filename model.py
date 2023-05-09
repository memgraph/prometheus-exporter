from typing import Dict, List

from prometheus_client import Gauge, Histogram

SIZE_CTR = Gauge("size_Gauge", 'Size Gauge description')
SIZE_GG = Gauge('size_gauge', 'Size gauge description')
HISTOGRAM = Histogram('histie', 'Histogram description')

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
    "LabelIndexCreated": Gauge("LabelIndexCreated", "Number of times a label index was created."),
    "LabelPropertyIndexCreated": Gauge("LabelPropertyIndexCreated", "Number of times a label property index was created.")
}

OPERATOR = {
  "AccumulateOperator": Gauge("AccumulateOperator", 'Number of times AccumulateOperator has been called'),
  "AggregateOperator": Gauge("AggregateOperator", 'Number of times AggregateOperator has been called'),
  "ApplyOperator": Gauge("ApplyOperator", 'Number of times ApplyOperator has been called'),
  "CallProcedureOperator": Gauge("CallProcedureOperator", 'Number of times CallProcedureOperator has been called'),
  "CartesianOperator": Gauge("CartesianOperator", 'Number of times CartesianOperator has been called'),
  "ConstructNamedPathOperator": Gauge("ConstructNamedPathOperator", 'Number of times ConstructNamedPathOperator has been called'),
  "CreateExpandOperator": Gauge("CreateExpandOperator", 'Number of times CreateExpandOperator has been called'),
  "CreateNodeOperator": Gauge("CreateNodeOperator", 'Number of times CreateNodeOperator has been called'),
  "DeleteOperator": Gauge("DeleteOperator", 'Number of times DeleteOperator has been called'),
  "DistinctOperator": Gauge("DistinctOperator", 'Number of times DistinctOperator has been called'),
  "EdgeUniquenessFilterOperator": Gauge("EdgeUniquenessFilterOperator", 'Number of times EdgeUniquenessFilterOperator has been called'),
  "EmptyResultOperator": Gauge("EmptyResultOperator", 'Number of times EmptyResultOperator has been called'),
  "EvaluatePatternFilterOperator": Gauge("EvaluatePatternFilterOperator", 'Number of times EvaluatePatternFilterOperator has been called'),
  "ExpandOperator": Gauge("ExpandOperator", 'Number of times ExpandOperator has been called'),
  "ExpandVariableOperator": Gauge("ExpandVariableOperator", 'Number of times ExpandVariableOperator has been called'),
  "FilterOperator": Gauge("FilterOperator", 'Number of times FilterOperator has been called'),
  "ForeachOperator": Gauge("ForeachOperator", 'Number of times ForeachOperator has been called'),
  "LimitOperator": Gauge("LimitOperator", 'Number of times LimitOperator has been called'),
  "MergeOperator": Gauge("MergeOperator", 'Number of times MergeOperator has been called'),
  "OnceOperator": Gauge("OnceOperator", 'Number of times OnceOperator has been called'),
  "OptionalOperator": Gauge("OptionalOperator", 'Number of times OptionalOperator has been called'),
  "OrderByOperator": Gauge("OrderByOperator", 'Number of times OrderByOperator has been called'),
  "ProduceOperator": Gauge("ProduceOperator", 'Number of times ProduceOperator has been called'),
  "RemoveLabelsOperator": Gauge("RemoveLabelsOperator", 'Number of times RemoveLabelsOperator has been called'),
  "RemovePropertyOperator": Gauge("RemovePropertyOperator", 'Number of times RemovePropertyOperator has been called'),
  "ScanAllByIdOperator": Gauge("ScanAllByIdOperator", 'Number of times ScanAllByIdOperator has been called'),
  "ScanAllByLabelOperator": Gauge("ScanAllByLabelOperator", 'Number of times ScanAllByLabelOperator has been called'),
  "ScanAllByLabelPropertyOperator": Gauge("ScanAllByLabelPropertyOperator", 'Number of times ScanAllByLabelPropertyOperator has been called'),
  "ScanAllByLabelPropertyRangeOperator": Gauge("ScanAllByLabelPropertyRangeOperator", 'Number of times ScanAllByLabelPropertyRangeOperator has been called'),
  "ScanAllByLabelPropertyValueOperator": Gauge("ScanAllByLabelPropertyValueOperator", 'Number of times ScanAllByLabelPropertyValueOperator has been called'),
  "ScanAllOperator": Gauge("ScanAllOperator", 'Number of times ScanAllOperator has been called'),
  "SetLabelsOperator": Gauge("SetLabelsOperator", 'Number of times SetLabelsOperator has been called'),
  "SetPropertiesOperator": Gauge("SetPropertiesOperator", 'Number of times SetPropertiesOperator has been called'),
  "SetPropertyOperator": Gauge("SetPropertyOperator", 'Number of times SetPropertyOperator has been called'),
  "SkipOperator": Gauge("SkipOperator", 'Number of times SkipOperator has been called'),
  "UnionOperator": Gauge("UnionOperator", 'Number of times UnionOperator has been called'),
  "UnwindOperator": Gauge("UnwindOperator", 'Number of times UnwindOperator has been called')
}

QUERY = {
  "QueryExecutionLatency_us_0p": Gauge("QueryExecutionLatency_us_0p", "Query execution latency in microseconds, 0th percentile"),
  "QueryExecutionLatency_us_100p": Gauge("QueryExecutionLatency_us_100p", "Query execution latency in microseconds, 100th percentile"),
  "QueryExecutionLatency_us_25p": Gauge("QueryExecutionLatency_us_25p", "Query execution latency in microseconds, 25th percentile"),
  "QueryExecutionLatency_us_50p": Gauge("QueryExecutionLatency_us_50p", "Query execution latency in microseconds, 50th percentile"),
  "QueryExecutionLatency_us_75p": Gauge("QueryExecutionLatency_us_75p", "Query execution latency in microseconds, 75th percentile"),
  "QueryExecutionLatency_us_99p": Gauge("QueryExecutionLatency_us_99p", "Query execution latency in microseconds, 99th percentile") 
}

QUERY_TYPE = {
  "ReadQuery": Gauge("ReadQuery", "Number of read-only queries executed."),
  "ReadWriteQuery": Gauge("ReadWriteQuery", "Number of write-only queries executed."),
  "WriteQuery": Gauge("WriteQuery", "Number of read-write queries executed.")
}

SESSION = {
  "ActiveBoltSessions": Gauge("ActiveBoltSessions", "Number of active connections."),
  "ActiveSSLSessions": Gauge("ActiveSSLSessions", "Number of active Bolt connections."),
  "ActiveSessions": Gauge("ActiveSessions", "Number of active TCP connections."),
  "ActiveTCPSessions": Gauge("ActiveTCPSessions", "Number of active TCP connections."),
  "ActiveWebSocketSessions": Gauge("ActiveWebSocketSessions", "Number of active websocket connections."),
  "BoltMessages": Gauge("BoltMessages", "Number of Bolt messages sent.")
}

SNAPSHOT = {
  "SnapshotCreationLatency_us_100p": Gauge("SnapshotCreationLatency_us_100p", "Snapshot creation latency in microseconds, 100th percentile") ,
  "SnapshotCreationLatency_us_50p": Gauge("SnapshotCreationLatency_us_50p", "Snapshot creation latency in microseconds, 50th percentile") ,
  "SnapshotCreationLatency_us_90p": Gauge("SnapshotCreationLatency_us_90p", "Snapshot creation latency in microseconds, 90th percentile") 
}

STREAM = {
  "MessagesConsumed": Gauge("MessagesConsumed", "Number of consumed streamed messages."),
  "StreamsCreated": Gauge("StreamsCreated", "Number of Streams created.")
}

TRANSACTION = {
  "ActiveTransactions": Gauge("ActiveTransactions", "Number of active transactions."),
  "CommitedTransactions": Gauge("CommitedTransactions", "Number of committed transactions."),
  "FailedQuery": Gauge("FailedQuery", "Number of times executing a query failed."),
  "RollbackedTransactions": Gauge("RollbackedTransactions", "Number of rollbacked transactions.")
}

TRIGGER = {
  "TriggersCreated": Gauge("TriggersCreated", "Number of Triggers created."),
  "TriggersExecuted": Gauge("TriggersExecuted", "Number of Triggers executed.")
}

GENERAL = {
  "average_degree": Gauge("average_degree", "Average node degree."),
  "disk_usage": Gauge("disk_usage", "Amount of disk usage."),
  "edge_count": Gauge("edge_count", "Edge count."),
  "memory_usage": Gauge("memory_usage", "Amount of memory usage."),
  "vertex_count": Gauge("vertex_count", "Vertex count.")
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


