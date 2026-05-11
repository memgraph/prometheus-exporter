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
from metrics.constraint_metrics import constraint_data
from metrics.schema_storage_metrics import schema_info_data, storage_info_data
from metrics.memory_metrics import memory_data

logger = logging.getLogger("prometheus_handler")


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
PrometheusConstraintData = {name: Gauge(name, description) for name, description in constraint_data}
PrometheusSchemaInfoData = {name: Gauge(name, description) for name, description in schema_info_data}
PrometheusStorageInfoData = {name: Gauge(name, description) for name, description in storage_info_data}
PrometheusMemoryData = {name: Gauge(name, description) for name, description in memory_data}


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
            mg_data.get("Index", {}),
            PrometheusIndexData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data.get("Operator", {}),
            PrometheusOperatorData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data.get("Query", {}),
            PrometheusQueryData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data.get("QueryType", {}),
            PrometheusQueryTypeData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data.get("Session", {}),
            PrometheusSessionData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data.get("Snapshot", {}),
            PrometheusSnapshotData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data.get("Stream", {}),
            PrometheusStreamData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data.get("Transaction", {}),
            PrometheusTransactionData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data.get("Trigger", {}),
            PrometheusTriggerData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data.get("TTL", {}),
            PrometheusTTLData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data.get("General", {}),
            PrometheusGeneralData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data.get("Constraint", {}),
            PrometheusConstraintData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data.get("SchemaInfo", {}),
            PrometheusSchemaInfoData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data.get("StorageInfo", {}),
            PrometheusStorageInfoData,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data.get("Memory", {}),
            PrometheusMemoryData,
        )
    )
