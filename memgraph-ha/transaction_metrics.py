from prometheus_client import Gauge

_data = [
    ("ActiveTransactions", "Number of active transactions."),
    ("CommitedTransactions", "Number of committed transactions."),
    ("FailedPrepare", "Number of failed prepare queries."),
    ("FailedPull", "Number of failed pulls."),
    ("FailedQuery", "Number of times executing a query failed."),
    ("RollbackedTransactions", "Number of rollbacked transactions."),
    ("SuccessfulQuery", "Number of successful queries"),
]


PrometheusTransactionData = {name: Gauge(name, description, ["instance_name"]) for name, description in _data}
