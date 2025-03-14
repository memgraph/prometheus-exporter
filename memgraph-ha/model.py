from functools import partial
import logging
import sys
from typing import Dict

from general_metrics import PrometheusGeneralData
from trigger_metrics import PrometheusTriggerData
from transaction_metrics import PrometheusTransactionData
from session_metrics import PrometheusSessionData
from ttl_metrics import PrometheusTTLData
from stream_metrics import PrometheusStreamData
from snapshot_metrics import PrometheusSnapshotData
from query_type_metrics import PrometheusQueryTypeData
from query_metrics import PrometheusQueryData
from index_metrics import PrometheusIndexData
from operator_metrics import PrometheusOperatorData
from ha_metrics import PrometheusHADataInstancesMetrics


logger = logging.getLogger("prometheus_handler")
logger.setLevel(logging.INFO)


def safe_execute(func):
    try:
        func()
    except Exception as e:
        logger.error("Error occurred while updating metrics: %s", e)


def update_prom_metrics_per_instance(mg_data, prom_data, instance_name):
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
            update_prom_metrics_per_instance,
            mg_data["Index"],
            PrometheusIndexData,
            instance_name,
        )
    )
    safe_execute(
        partial(
            update_prom_metrics_per_instance,
            mg_data["Operator"],
            PrometheusOperatorData,
            instance_name,
        )
    )
    safe_execute(
        partial(
            update_prom_metrics_per_instance,
            mg_data["Query"],
            PrometheusQueryData,
            instance_name,
        )
    )
    safe_execute(
        partial(
            update_prom_metrics_per_instance,
            mg_data["QueryType"],
            PrometheusQueryTypeData,
            instance_name,
        )
    )
    safe_execute(
        partial(
            update_prom_metrics_per_instance,
            mg_data["Session"],
            PrometheusSessionData,
            instance_name,
        )
    )
    safe_execute(
        partial(
            update_prom_metrics_per_instance,
            mg_data["Snapshot"],
            PrometheusSnapshotData,
            instance_name,
        )
    )
    safe_execute(
        partial(
            update_prom_metrics_per_instance,
            mg_data["Stream"],
            PrometheusStreamData,
            instance_name,
        )
    )
    safe_execute(
        partial(
            update_prom_metrics_per_instance,
            mg_data["Transaction"],
            PrometheusTransactionData,
            instance_name,
        )
    )
    safe_execute(
        partial(
            update_prom_metrics_per_instance,
            mg_data["Trigger"],
            PrometheusTriggerData,
            instance_name,
        )
    )
    safe_execute(
        partial(
            update_prom_metrics_per_instance,
            mg_data["TTL"],
            PrometheusTTLData,
            instance_name,
        )
    )
    safe_execute(
        partial(
            update_prom_metrics_per_instance,
            mg_data["General"],
            PrometheusGeneralData,
            instance_name,
        )
    )

    safe_execute(
        partial(
            update_prom_metrics_per_instance,
            mg_data["HighAvailability"],
            PrometheusHADataInstancesMetrics,
            instance_name,
        )
    )


def update_coordinator_metrics(mg_data, instance_name):
    safe_execute(
        partial(
            update_prom_metrics_per_instance,
            mg_data["General"],
            PrometheusGeneralData,
            instance_name,
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
