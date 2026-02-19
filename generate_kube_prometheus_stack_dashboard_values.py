#!/usr/bin/env python3
"""
Wrap a Grafana dashboard JSON into a kube-prometheus-stack values YAML.

It uses kube-prometheus-stack `extraManifests` to ship a ConfigMap labelled for
Grafana's dashboard sidecar:
  grafana.sidecar.dashboards.label: grafana_dashboard
  grafana.sidecar.dashboards.labelValue: "1"

Usage:
  ./generate_kube_prometheus_stack_dashboard_values.py \
    --dashboard-json memgraph-grafana-dashboard.json \
    --out kube_prometheus_stack_memgraph_dashboard.yaml
"""

from __future__ import annotations

import argparse
from pathlib import Path


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dashboard-json",
        default="memgraph-grafana-dashboard.json",
        help="Path to the Grafana dashboard JSON file.",
    )
    parser.add_argument(
        "--out",
        default="kube_prometheus_stack_memgraph_dashboard.yaml",
        help="Output values YAML path.",
    )
    parser.add_argument(
        "--namespace",
        default="monitoring",
        help="Namespace where Grafana is running (usually 'monitoring').",
    )
    parser.add_argument(
        "--configmap-name",
        default="memgraph-grafana-dashboard",
        help="Name of the ConfigMap to create.",
    )
    parser.add_argument(
        "--manifest-key",
        default="memgraphGrafanaDashboard",
        help="Key under extraManifests (useful for merging multiple values files).",
    )
    args = parser.parse_args()

    dashboard_path = Path(args.dashboard_json)
    out_path = Path(args.out)

    dashboard_json = dashboard_path.read_text(encoding="utf-8")
    # Ensure trailing newline inside the block.
    if not dashboard_json.endswith("\n"):
        dashboard_json += "\n"

    # Escape any Grafana/Prometheus legend templates like `{{__name__}}` so Helm
    # doesn't try to interpret them when processing extraManifests via `tpl`.
    dashboard_json = _escape_for_helm_tpl(dashboard_json)

    json_key = dashboard_path.name
    if not json_key.endswith(".json"):
        json_key = f"{json_key}.json"

    # YAML structure:
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
    yaml_text = f"""extraManifests:
  {args.manifest_key}:
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: {args.configmap_name}
      namespace: {args.namespace}
      labels:
        grafana_dashboard: "1"
    data:
      {json_key}: |
{_indent_block(dashboard_json.rstrip('\\n'), 8)}
"""

    out_path.write_text(yaml_text, encoding="utf-8")


if __name__ == "__main__":
    main()


