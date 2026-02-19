#!/usr/bin/env python3
"""
Generate a Grafana dashboard JSON for the Memgraph Prometheus exporter.

"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, Union

# Allow running this script from the repo root by adding the Prometheus exporter
# package path (which contains the `metrics/` module) to PYTHONPATH.
_REPO_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_DIR))

from metrics.general_metrics import general_data
from metrics.ha_metrics import (
    ha_coordinator_metrics,
    ha_coordinators_agg_metrics,
    ha_data_instances_counter_metrics,
    ha_data_instances_metrics,
)
from metrics.index_metrics import index_data
from metrics.operator_metrics import operator_data
from metrics.query_metrics import query_data
from metrics.query_type_metrics import query_type_data
from metrics.session_metrics import session_data
from metrics.snapshot_metrics import snapshot_data
from metrics.stream_metrics import stream_data
from metrics.transaction_metrics import txn_data
from metrics.trigger_metrics import trigger_data
from metrics.ttl_metrics import ttl_data


MetricDef = Union[str, Tuple[str, str]]


@dataclass(frozen=True)
class MetricGroup:
    title: str
    metrics: Sequence[MetricDef]
    # "gauge" metrics are queried directly; "counter" metrics are queried via rate(<name>_total[]).
    kind: str = "gauge"  # "gauge" | "counter"
    legend_format: str = "__auto"


_LATENCY_RE = re.compile(r"^(?P<base>.+)_us_(?P<pct>\d+)p$")

LEGEND_NON_HA = "{{__name__}} (instance={{instance}})"
LEGEND_HA = "{{__name__}} (instance_name={{instance_name}})"
LEGEND_BOTH = "{{__name__}} (instance_name={{instance_name}}, instance={{instance}})"

# "Auto" legend support:
# - In HA mode, exporter metrics include `instance_name`, so we want to show that.
# - In standalone mode, metrics do NOT include `instance_name`, so we fall back to a
#   fixed string (e.g. "memgraph") instead of showing exporter pod IPs.
#
# We implement this by adding a derived label `mg_instance` in the PromQL expression:
# 1) set mg_instance=<fallback> for all series (based on an always-present label like `instance`)
# 2) override mg_instance=<instance_name> only for series that have `instance_name`
MG_INSTANCE_LABEL = "mg_instance"
LEGEND_INSTANCE_NAME_AUTO = "{{__name__}} (instance_name={{mg_instance}})"

PANEL_COLS = 4
PANEL_W = 24 // PANEL_COLS  # 6
PANEL_H = 8


def _metric_name(m: MetricDef) -> str:
    return m if isinstance(m, str) else m[0]


def _metric_desc(m: MetricDef) -> str:
    return "" if isinstance(m, str) else (m[1] or "")


def _split_camel(s: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", s)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", s)
    return s


def _title_case_snake(s: str) -> str:
    return " ".join([part for part in s.split("_") if part]).strip().title()


def _normalize_acronyms(s: str) -> str:
    replacements = {
        "Rpc": "RPC",
        "Wal": "WAL",
        "Ssl": "SSL",
        "Tcp": "TCP",
        "Uuid": "UUID",
        "Ha": "HA",
        "Ttl": "TTL",
        "Web Socket": "WebSocket",
    }
    for src, dst in replacements.items():
        s = re.sub(rf"\b{re.escape(src)}\b", dst, s)
    return s


def _nice_title_for_metric(name: str) -> str:
    m = _LATENCY_RE.match(name)
    if m:
        base = m.group("base")
        pct = m.group("pct")
        base_title = _normalize_acronyms(_split_camel(base)).strip()
        return f"{base_title} (p{pct})"

    if "_" in name:
        return _normalize_acronyms(_title_case_snake(name))

    return _normalize_acronyms(_split_camel(name)).strip()


def _build_title_map() -> Dict[str, str]:
    metric_names: List[str] = []

    def add_metrics(ms: Sequence[MetricDef]) -> None:
        for m in ms:
            metric_names.append(_metric_name(m))

    add_metrics(general_data)
    add_metrics(index_data)
    add_metrics(query_data)
    add_metrics(query_type_data)
    add_metrics(session_data)
    add_metrics(snapshot_data)
    add_metrics(stream_data)
    add_metrics(txn_data)
    add_metrics(trigger_data)
    add_metrics(ttl_data)
    metric_names.extend(list(operator_data))
    add_metrics(ha_data_instances_metrics)
    add_metrics(ha_data_instances_counter_metrics)
    add_metrics(ha_coordinator_metrics)
    add_metrics(ha_coordinators_agg_metrics)

    out: Dict[str, str] = {}
    for name in metric_names:
        out[name] = _nice_title_for_metric(name)
    return out


TITLE_MAP: Dict[str, str] = _build_title_map()


def _infer_unit(name: str) -> Optional[str]:
    if _LATENCY_RE.match(name):
        return "s"

    lower = name.lower()
    if "memory_usage" in lower or "disk_usage" in lower:
        return "bytes"

    return "sishort"


def _row_panel(*, panel_id: int, title: str, y: int) -> dict:
    return {
        "collapsed": False,
        "gridPos": {"h": 1, "w": 24, "x": 0, "y": y},
        "id": panel_id,
        "panels": [],
        "title": title,
        "type": "row",
    }


def _timeseries_panel(
    *,
    panel_id: int,
    title: str,
    description: str,
    expr: str,
    y: int,
    x: int,
    unit: Optional[str],
    legend_format: str,
    w: int = PANEL_W,
    h: int = PANEL_H,
    datasource_uid: str = "prometheus",
) -> dict:
    defaults: dict = {
        "color": {"mode": "palette-classic"},
        "custom": {
            "axisBorderShow": False,
            "axisCenteredZero": False,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "barWidthFactor": 0.6,
            "drawStyle": "line",
            "fillOpacity": 0,
            "gradientMode": "none",
            "hideFrom": {"legend": False, "tooltip": False, "viz": False},
            "insertNulls": False,
            "lineInterpolation": "smooth",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {"type": "linear"},
            "showPoints": "auto",
            "showValues": False,
            "spanNulls": False,
            "stacking": {"group": "A", "mode": "none"},
            "thresholdsStyle": {"mode": "off"},
        },
        "mappings": [],
        "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": 0}]},
    }
    if unit is not None:
        defaults["unit"] = unit

    return {
        "datasource": {"type": "prometheus", "uid": datasource_uid},
        "description": description,
        "fieldConfig": {"defaults": defaults, "overrides": []},
        "gridPos": {"h": h, "w": w, "x": x, "y": y},
        "id": panel_id,
        "options": {
            "legend": {
                "calcs": [],
                "displayMode": "list",
                "placement": "bottom",
                "showLegend": True,
            },
            "tooltip": {"hideZeros": False, "mode": "single", "sort": "none"},
        },
        "pluginVersion": "12.3.3",
        "targets": [
            {
                "datasource": {"type": "prometheus", "uid": datasource_uid},
                "editorMode": "builder",
                "expr": expr,
                "legendFormat": legend_format,
                "range": True,
                "refId": "A",
            }
        ],
        "title": title,
        "type": "timeseries",
    }


def _templating() -> dict:
    return {
        "list": [
            {
                "current": {"selected": False, "text": "All", "value": "$__all"},
                "datasource": {"type": "prometheus", "uid": "prometheus"},
                # Use a Memgraph metric (not `up`) so instance/job lists include
                # series that existed within the dashboard time range, even if the
                # target is no longer active at "now" (e.g. after restarts).
                "definition": "label_values(edge_count, job)",
                "hide": 0,
                "includeAll": True,
                # Make "All" truly match all series, not just the enumerated options.
                "allValue": ".*",
                "label": "job",
                "multi": True,
                "name": "job",
                "options": [],
                "query": {
                    "query": "label_values(edge_count, job)",
                    "refId": "PrometheusVariableQueryEditor-VariableQuery",
                },
                # Refresh on time range change so options track the dashboard window.
                "refresh": 2,
                "regex": "",
                "skipUrlSync": False,
                "sort": 1,
                "type": "query",
            },
            {
                "current": {"selected": False, "text": "All", "value": "$__all"},
                "datasource": {"type": "prometheus", "uid": "prometheus"},
                "definition": 'label_values(edge_count{job=~"$job"}, instance)',
                "hide": 0,
                "includeAll": True,
                "allValue": ".*",
                "label": "instance",
                "multi": True,
                "name": "instance",
                "options": [],
                "query": {
                    "query": 'label_values(edge_count{job=~"$job"}, instance)',
                    "refId": "PrometheusVariableQueryEditor-VariableQuery",
                },
                "refresh": 2,
                "regex": "",
                "skipUrlSync": False,
                "sort": 1,
                "type": "query",
            },
        ]
    }


def _prom_escape_string_literal(s: str) -> str:
    # Escape for PromQL double-quoted string literal.
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _with_mg_instance(expr: str, *, fallback: str) -> str:
    fallback = _prom_escape_string_literal(fallback)
    # Always set MG_INSTANCE_LABEL to a fallback value.
    out = f'label_replace({expr}, "{MG_INSTANCE_LABEL}", "{fallback}", "instance", ".*")'
    # If `instance_name` exists, override MG_INSTANCE_LABEL with its value.
    # Note: if a label is missing, Prometheus treats its value as an empty string.
    # Using (.*) would match that and overwrite the fallback with "", so require non-empty.
    out = f'label_replace({out}, "{MG_INSTANCE_LABEL}", "$1", "instance_name", "(.+)")'
    return out


def _prom_expr_for_metric(*, name: str, kind: str) -> str:
    selector = '{job=~"$job", instance=~"$instance"}'

    if _LATENCY_RE.match(name):
        return f"({name}{selector}) / 1e6"

    if kind == "counter":
        return f'rate({name}_total{selector}[$__rate_interval])'

    return f"{name}{selector}"


def build_dashboard(
    *,
    groups: Sequence[MetricGroup],
    add_mg_instance: bool = False,
    mg_instance_fallback: str = "memgraph",
) -> dict:
    panels: List[dict] = []
    panel_id = 1
    y = 0

    for group in groups:
        panels.append(_row_panel(panel_id=panel_id, title=group.title, y=y))
        panel_id += 1
        y += 1

        i = 0
        line_y = y
        for m in group.metrics:
            x = (i % PANEL_COLS) * PANEL_W
            if i > 0 and i % PANEL_COLS == 0:
                line_y += PANEL_H

            metric = _metric_name(m)
            desc = _metric_desc(m)

            expr = _prom_expr_for_metric(name=metric, kind=group.kind)
            if add_mg_instance:
                expr = _with_mg_instance(expr, fallback=mg_instance_fallback)
            unit = _infer_unit(metric)
            title = TITLE_MAP.get(metric, metric)

            panels.append(
                _timeseries_panel(
                    panel_id=panel_id,
                    title=title,
                    description=desc,
                    expr=expr,
                    y=line_y,
                    x=x,
                    unit=unit,
                    legend_format=group.legend_format,
                )
            )
            panel_id += 1
            i += 1

        if len(group.metrics) > 0:
            lines = (len(group.metrics) + PANEL_COLS - 1) // PANEL_COLS
            y = y + (lines * PANEL_H)

    return {
        "annotations": {
            "list": [
                {
                    "builtIn": 1,
                    "datasource": {"type": "grafana", "uid": "-- Grafana --"},
                    "enable": True,
                    "hide": True,
                    "iconColor": "rgba(0, 211, 255, 1)",
                    "name": "Annotations & Alerts",
                    "type": "dashboard",
                }
            ]
        },
        "editable": True,
        "fiscalYearStartMonth": 0,
        "graphTooltip": 0,
        "id": 0,
        "links": [],
        "panels": panels,
        "preload": False,
        "schemaVersion": 42,
        "tags": ["memgraph", "prometheus-exporter"],
        "templating": _templating(),
        "time": {"from": "now-6h", "to": "now"},
        "timepicker": {},
        "timezone": "browser",
        "title": "Memgraph",
        "uid": "memgraph-prometheus-exporter",
        "version": 1,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="memgraph-grafana-dashboard.json",
        help="Output dashboard JSON path (relative to current directory).",
    )
    parser.add_argument(
        "--non-ha-legend-label",
        choices=["auto", "instance", "instance_name", "both"],
        default="auto",
        help=(
            "Which Prometheus label(s) to show in panel legends for non-HA metric groups. "
            "'instance' is the scrape target address (often <pod-ip>:<port>). "
            "For the Memgraph HA exporter, metrics typically include 'instance_name' (e.g. data0). "
            "'auto' shows instance_name when present, otherwise falls back to a fixed string "
            "(see --standalone-instance-name)."
        ),
    )
    parser.add_argument(
        "--standalone-instance-name",
        default="memgraph",
        help=(
            "Fallback name to show in legends when `instance_name` isn't present "
            "(e.g. when scraping the standalone exporter). Used with --non-ha-legend-label=auto."
        ),
    )
    args = parser.parse_args()

    add_mg_instance = args.non_ha_legend_label == "auto"
    legend_non_ha = {
        "instance": LEGEND_NON_HA,
        "instance_name": LEGEND_HA,
        "both": LEGEND_BOTH,
        "auto": LEGEND_INSTANCE_NAME_AUTO,
    }[args.non_ha_legend_label]

    groups: List[MetricGroup] = [
        MetricGroup("General metrics", general_data, legend_format=legend_non_ha),
        MetricGroup("Index metrics", index_data, legend_format=legend_non_ha),
        MetricGroup("Operator metrics", operator_data, legend_format=legend_non_ha),
        MetricGroup("Query metrics", query_data, legend_format=legend_non_ha),
        MetricGroup("Query type metrics", query_type_data, legend_format=legend_non_ha),
        MetricGroup("Session metrics", session_data, legend_format=legend_non_ha),
        MetricGroup("Snapshot metrics", snapshot_data, legend_format=legend_non_ha),
        MetricGroup("Stream metrics", stream_data, legend_format=legend_non_ha),
        MetricGroup("Transaction metrics", txn_data, legend_format=legend_non_ha),
        MetricGroup("Trigger metrics", trigger_data, legend_format=legend_non_ha),
        MetricGroup("TTL metrics", ttl_data, legend_format=legend_non_ha),
        MetricGroup(
            "HA data instances — latency (p50/p90/p99)",
            ha_data_instances_metrics,
            kind="gauge",
            legend_format=LEGEND_HA,
        ),
        MetricGroup(
            "HA data instances — counters (rate/s)",
            ha_data_instances_counter_metrics,
            kind="counter",
            legend_format=LEGEND_HA,
        ),
        MetricGroup(
            "HA coordinators — latency (p50/p90/p99)",
            ha_coordinator_metrics,
            kind="gauge",
            legend_format=LEGEND_HA,
        ),
        MetricGroup(
            "HA coordinators — aggregate counters (rate/s)",
            ha_coordinators_agg_metrics,
            kind="counter",
            # These don't have `instance_name`.
            legend_format=LEGEND_NON_HA
            if args.non_ha_legend_label == "instance_name"
            else legend_non_ha,
        ),
    ]

    dashboard = build_dashboard(
        groups=groups,
        add_mg_instance=add_mg_instance,
        mg_instance_fallback=args.standalone_instance_name,
    )
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(dashboard, f, indent=2, sort_keys=False)
        f.write("\n")


if __name__ == "__main__":
    main()


