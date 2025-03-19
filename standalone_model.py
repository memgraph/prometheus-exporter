from functools import partial
import logging
from typing import Dict

from prometheus_client import Gauge

from metrics.general_metrics import general_data
from metrics.trigger_metrics import trigger_data
from metrics.transaction_metrics import txn_data
from metrics.session_metrics import session_data
from metrics.ttl_metrics import ttl_data
from metrics.stream_metrics import stream_data
from metrics.snapshot_metrics import snapshot_data
from metrics.query_type_metrics import query_type_data
from metrics.query_metrics import query_data
from metrics.index_metrics import index_data
from metrics.operator_metrics import operator_data

logger = logging.getLogger("prometheus_handler")
logger.setLevel(logging.INFO)


PrometheusIndexData = {name: Gauge(name, description) for name, description in index_data}
PrometheusGeneralData = {name: Gauge(name, description) for name, description in general_data}
PrometheusOperatorData = {name: Gauge(name, f"Number of times {name} has been called.") for name in operator_data}
PrometheusQueryData = {name: Gauge(name, description) for name, description in query_data}
PrometheusQueryTypeData = {name: Gauge(name, description) for name, description in query_type_data}
PrometheusSessionData = {name: Gauge(name, description) for name, description in session_data}
PrometheusSnapshotData = {name: Gauge(name, description) for name, description in snapshot_data}
PrometheusStreamData = {name: Gauge(name, description) for name, description in stream_data}
PrometheusTransactionData = {name: Gauge(name, description) for name, description in txn_data}
PrometheusTriggerData = {name: Gauge(name, description) for name, description in trigger_data}
PrometheusTTLData = {name: Gauge(name, description) for name, description in ttl_data}


def safe_execute(func):
    try:
        func()
    except Exception as e:
        logger.error("Error occurred while updating metrics: %s", e)


def update_gauges(mg_data, prom_data):
    for key, value in mg_data.items():
        if key not in prom_data:
            continue
        prom_data[key].set(value)


def update_metrics(mg_data: Dict[str, Dict[str, int]]):
    safe_execute(
        partial(
            update_gauges,
            mg_data["Index"],
            PrometheusIndexData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data["Operator"],
            PrometheusOperatorData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data["Query"],
            PrometheusQueryData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data["QueryType"],
            PrometheusQueryTypeData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data["Session"],
            PrometheusSessionData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data["Snapshot"],
            PrometheusSnapshotData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data["Stream"],
            PrometheusStreamData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data["Transaction"],
            PrometheusTransactionData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data["Trigger"],
            PrometheusTriggerData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data["TTL"],
            PrometheusTTLData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data["General"],
            PrometheusGeneralData,
        )
    )
