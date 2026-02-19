#!/usr/bin/env python3
"""
Wrap a Grafana dashboard JSON into a kube-prometheus-stack values YAML.

It uses kube-prometheus-stack `extraManifests` to ship a ConfigMap labelled for
Grafana's dashboard sidecar:
  grafana.sidecar.dashboards.label: grafana_dashboard
  grafana.sidecar.dashboards.labelValue: "1"

Optionally, it can also emit a `grafana:` values block (admin creds + NodePort
service) in the same values file, so you can `helm upgrade ... -f <out>`.

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


def _yaml_double_quote(value: str) -> str:
    # Minimal escaping for double-quoted YAML scalars.
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


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
    parser.add_argument(
        "--no-grafana-values",
        action="store_true",
        help="Do not include the `grafana:` admin/service block in the output values YAML.",
    )
    parser.add_argument(
        "--grafana-admin-user",
        default="admin",
        help="Grafana admin username to place under `grafana.adminUser`.",
    )
    parser.add_argument(
        "--grafana-admin-password",
        default="change-me",
        help="Grafana admin password to place under `grafana.adminPassword` (stored in values YAML).",
    )
    parser.add_argument(
        "--grafana-service-type",
        default="NodePort",
        help="Grafana service type to place under `grafana.service.type` (e.g. NodePort, ClusterIP, LoadBalancer).",
    )
    parser.add_argument(
        "--grafana-node-port",
        type=int,
        default=32000,
        help="Grafana service NodePort to place under `grafana.service.nodePort` (only meaningful for NodePort).",
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
    grafana_values = ""
    if not args.no_grafana_values:
        grafana_values = f"""grafana:
  # WARNING: This stores the admin password in a Helm values file.
  # Consider using `grafana.admin.existingSecret` for a safer setup.
  adminUser: {_yaml_double_quote(args.grafana_admin_user)}
  adminPassword: {_yaml_double_quote(args.grafana_admin_password)}

  service:
    # Expose Grafana outside the cluster:
    # - reachable at: http://<node-ip>:{args.grafana_node_port}
    # - binds on the node's network interfaces (effectively "0.0.0.0" on that node)
    type: {args.grafana_service_type}
    nodePort: {args.grafana_node_port}

"""

    yaml_text = f"""{grafana_values}extraManifests:
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


