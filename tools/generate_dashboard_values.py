#!/usr/bin/env python3
"""
Wrap a Grafana dashboard JSON into a kube-prometheus-stack values YAML.

It uses kube-prometheus-stack `extraManifests` to ship a ConfigMap labelled for
Grafana's dashboard sidecar:
  grafana.sidecar.dashboards.label: grafana_dashboard
  grafana.sidecar.dashboards.labelValue: "1"

Usage:
  python3 tools/generate_dashboard_values.py \
    --dashboard-json dashboards/memgraph_prometheus.json \
    --out dashboards/memgraph_prometheus.yaml
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable


def _indent_block(text: str, spaces: int) -> str:
    prefix = " " * spaces
    # Preserve empty lines as well.
    return "\n".join(prefix + line for line in text.splitlines())

def _escape_for_helm_tpl(text: str) -> str:
    """
    kube-prometheus-stack renders `extraManifests` via Helm `tpl`, so any `{{ ... }}`
    inside the embedded JSON is treated as a Go template expression and will fail.

    We escape literal `{{` / `}}` so Helm renders them back as plain braces.
    Example:
      '{{__name__}}' -> '{{ "{{" }}__name__{{ "}}" }}'
    """

    l_tok = "__HELM_LBRACE__"
    r_tok = "__HELM_RBRACE__"
    text = text.replace("{{", l_tok).replace("}}", r_tok)
    text = text.replace(l_tok, '{{ "{{" }}').replace(r_tok, '{{ "}}" }}')
    return text


def _yaml_double_quote(value: str) -> str:
    # Minimal escaping for double-quoted YAML scalars.
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _default_logs_dashboard(main_dashboard: Path) -> Path | None:
    # Pair known datasource-specific metric dashboards with their log dashboards.
    dashboard_to_logs = {
        "memgraph_victoriametrics.json": "memgraph_victorialogs.json",
        "memgraph_prometheus.json": "memgraph_loki.json",
        "memgraph_victoria.json": "memgraph_victorialogs.json",
        "memgraph-grafana-dashboard-victoriametrics.json": "memgraph_victorialogs.json",
        "memgraph-grafana-dashboard.json": "memgraph_loki.json",
    }
    logs_name = dashboard_to_logs.get(main_dashboard.name)
    if logs_name is None:
        return None
    return main_dashboard.with_name(logs_name)


def _load_dashboard_json(path: Path) -> str:
    dashboard_json = path.read_text(encoding="utf-8")
    # Ensure trailing newline inside the block.
    if not dashboard_json.endswith("\n"):
        dashboard_json += "\n"

    # Escape any Grafana/Prometheus legend templates like `{{__name__}}` so Helm
    # doesn't try to interpret them when processing extraManifests via `tpl`.
    return _escape_for_helm_tpl(dashboard_json)


def _dashboard_data_block(dashboard_paths: Iterable[Path]) -> str:
    data_entries = []
    for dashboard_path in dashboard_paths:
        dashboard_json = _load_dashboard_json(dashboard_path)
        json_key = dashboard_path.name
        if not json_key.endswith(".json"):
            json_key = f"{json_key}.json"
        data_entries.append(
            f"      {json_key}: |\n"
            f"{_indent_block(dashboard_json.rstrip('\\n'), 8)}"
        )
    return "\n".join(data_entries)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dashboard-json",
        default="dashboards/memgraph_prometheus.json",
        help="Path to the Grafana dashboard JSON file.",
    )
    parser.add_argument(
        "--out",
        default="dashboards/memgraph_prometheus.yaml",
        help="Output values YAML path.",
    )
    parser.add_argument(
        "--extra-dashboard-json",
        action="append",
        default=[],
        help=(
            "Additional Grafana dashboard JSON file to embed. "
            "Can be passed multiple times."
        ),
    )
    args = parser.parse_args()

    dashboard_path = Path(args.dashboard_json)
    out_path = Path(args.out)

    all_dashboard_paths = [dashboard_path]
    auto_logs_dashboard = _default_logs_dashboard(dashboard_path)
    if auto_logs_dashboard is not None and auto_logs_dashboard.exists():
        all_dashboard_paths.append(auto_logs_dashboard)
    all_dashboard_paths.extend(Path(path) for path in args.extra_dashboard_json)

    # Keep order stable and remove duplicates.
    unique_dashboard_paths = list(dict.fromkeys(all_dashboard_paths))

    # YAML structure:
    # grafana:
    #   service:
    #     type: LoadBalancer
    # extraManifests:
    #   <manifest-key>:
    #     apiVersion: v1
    #     kind: ConfigMap
    #     metadata:
    #       ...
    #     data:
    #       <dashboard.json>: |
    #         { ... }
    #
    # The JSON block content must be indented 8 spaces to sit under the `|`.
    #
    # Hard-coded defaults (kept intentionally simple):
    # - namespace: monitoring
    # - ConfigMap name: memgraph-grafana-dashboard
    # - extraManifests key: memgraphGrafanaDashboard
    # - Grafana service exposure: LoadBalancer
    yaml_text = f"""extraManifests:
  memgraphGrafanaDashboard:
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: memgraph-grafana-dashboard
      namespace: monitoring
      labels:
        grafana_dashboard: "1"
    data:
{_dashboard_data_block(unique_dashboard_paths)}
"""
    yaml_text = (
        "grafana:\n"
        "  service:\n"
        "    # Expose Grafana via a cloud LoadBalancer.\n"
        "    # For local/bare-metal clusters without a LB controller, switch to NodePort.\n"
        "    type: LoadBalancer\n"
        "\n"
        + yaml_text
    )

    out_path.write_text(yaml_text, encoding="utf-8")


if __name__ == "__main__":
    main()


