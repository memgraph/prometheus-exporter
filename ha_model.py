from functools import partial
import logging
import sys
from typing import Dict

from prometheus_client import Counter, Gauge

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
from metrics.ha_metrics import ha_data_instances_metrics, ha_coordinator_metrics, ha_coordinators_agg_metrics

# Metrics related to HA specific to each data instance
PrometheusHADataInstancesMetrics = {
    name: Gauge(name, description, ["instance_name"])
    for name, description in ha_data_instances_metrics
}
# Metrics specific to each coordinator
PrometheusHACoordinatorMetrics = {
    name: Gauge(name, description, ["instance_name"])
    for name, description in ha_coordinator_metrics
}
# Metrics common to all coordinators
PrometheusHACoordinatorsAggMetrics = {
    name: Counter(name, description) for name, description in ha_coordinators_agg_metrics
}

PrometheusIndexData = {name: Gauge(name, description, ["instance_name"]) for name, description in index_data}
PrometheusGeneralData = {name: Gauge(name, description, ["instance_name"]) for name, description in general_data}
PrometheusOperatorData = {name: Gauge(name, f"Number of times {name} has been called.", ["instance_name"]) for name in operator_data}
PrometheusQueryData = {name: Gauge(name, description, ["instance_name"]) for name, description in query_data}
PrometheusQueryTypeData = {name: Gauge(name, description, ["instance_name"]) for name, description in query_type_data}
PrometheusSessionData = {name: Gauge(name, description, ["instance_name"]) for name, description in session_data}
PrometheusSnapshotData = {name: Gauge(name, description, ["instance_name"]) for name, description in snapshot_data}
PrometheusStreamData = {name: Gauge(name, description, ["instance_name"]) for name, description in stream_data}
PrometheusTransactionData = {name: Gauge(name, description, ["instance_name"]) for name, description in txn_data}
PrometheusTriggerData = {name: Gauge(name, description, ["instance_name"]) for name, description in trigger_data}
PrometheusTTLData = {name: Gauge(name, description, ["instance_name"]) for name, description in ttl_data}


logger = logging.getLogger("prometheus_handler")


def safe_execute(func):
    try:
        func()
    except Exception as e:
        logger.error("Error occurred while updating metrics: %s", e)


def aggregate_gauges(mg_data, prom_data):
    """
    Aggregate gauge values.
    """
    for key, value in mg_data.items():
        if key not in prom_data:
            continue
        prom_data[key].inc(amount=value)


def update_gauges(mg_data, prom_data, instance_name):
    """
    Updates metrics on Prometheus which are specific to an instance. Metrics specific to an instance are labeled with 'instance_name'.
    """
    for key, value in mg_data.items():
        if key not in prom_data:
            continue
        prom_data[key].labels(instance_name=instance_name).set(value)


def update_data_instance_metrics(mg_data, instance_name):
    safe_execute(
        partial(
            update_gauges,
            mg_data["Index"],
            PrometheusIndexData,
            instance_name,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data["Operator"],
            PrometheusOperatorData,
            instance_name,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data["Query"],
            PrometheusQueryData,
            instance_name,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data["QueryType"],
            PrometheusQueryTypeData,
            instance_name,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data["Session"],
            PrometheusSessionData,
            instance_name,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data["Snapshot"],
            PrometheusSnapshotData,
            instance_name,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data["Stream"],
            PrometheusStreamData,
            instance_name,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data["Transaction"],
            PrometheusTransactionData,
            instance_name,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data["Trigger"],
            PrometheusTriggerData,
            instance_name,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data["TTL"],
            PrometheusTTLData,
            instance_name,
        )
    )
    safe_execute(
        partial(
            update_gauges,
            mg_data["General"],
            PrometheusGeneralData,
            instance_name,
        )
    )

    safe_execute(
        partial(
            update_gauges,
            mg_data["HighAvailability"],
            PrometheusHADataInstancesMetrics,
            instance_name,
        )
    )


def update_coordinator_metrics(mg_data, instance_name):
    safe_execute(
        partial(
            update_gauges,
            mg_data["General"],
            PrometheusGeneralData,
            instance_name,
        )
    )

    safe_execute(
        partial(
            update_gauges,
            mg_data["HighAvailability"],
            PrometheusHACoordinatorMetrics,
            instance_name,
        )
    )

    safe_execute(
        partial(
            aggregate_gauges,
            mg_data["HighAvailability"],
            PrometheusHACoordinatorsAggMetrics,
        )
    )


def update_metrics(mg_data: Dict[str, Dict[str, int]], instance):
    """
    Updates data on Prometheus based on metrics received for instance 'instance'.
    Parameters:
    mg_data: Data received from Memgraph instance with name 'instance_name'.
    instance: The instance whose data is being processed.
    """
    if instance.type == "data_instance":
        update_data_instance_metrics(mg_data, instance.name)
    elif instance.type == "coordinator":
        update_coordinator_metrics(mg_data, instance.name)
    else:
        logger.error("Unknown instance type %s", instance.type)
        sys.exit(-1)
