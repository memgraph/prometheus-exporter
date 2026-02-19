# Memgraph metrics exporter

[Memgraph](https://github.com/memgraph/memgraph) exporter for Prometheus.

The metrics currently collected can be found [in the documentation](https://memgraph.com/docs/configuration/monitoring-server#monitoring-via-http-server-enterprise).

## Running the exporter as Python script

```shell
$ git clone https://github.com/memgraph/prometheus-exporter.git
$ cd prometheus-exporter
$ python3 -m pip install requests prometheus_client
$ python3 mg_exporter.py --type={standalone,HA} --config-file=config_file.yaml
```

### Standalone exporter

Standalone exporter can attach only to the single Memgraph instance. It can be started by running:

```bash
python3 mg_exporter.py --type=standalone --config-file=/code/standalone_config.yaml
```
The file `standalone_config.yaml` serves as a template for your configuration file when running in standalone mode.

Make sure to adjust host and port in `standalone_config.yaml`.


### HA exporter

High availability exporter attaches to multiple memgraph instances which are connected in cluster. It exposes for each instance all metrics
which are exposed through standalone exporter but it also adds HA metrics. The full list of metrics used can be found on [here](https://memgraph.com/docs/database-management/monitoring#ha-metrics).

```bash
python3 mg_exporter.py --type=HA --config-file=/code/ha_config.yaml
```

The file `ha_config.yaml` serves as a template for your configuration file when running in HA mode.

Make sure to adjust url and port for each instance in the cluster in `ha_config.yaml` file.

## Running through Docker

The code is also available on DockerHub as `memgraph/prometheus-exporter`.

```bash
docker run -e DEPLOYMENT_TYPE=HA -e CONFIG_FILE=/etc/ha_config.yaml memgraph/prometheus-exporter
```

## Running and Debugging the Setup

1. Startup your local Memgraph instance.
2. Make sure Memgraph is sending the metric information
```shell
$ curl <<MEMGRAPH_METRICS_HOST>>:<<MEMGRAPH_METRICS_PORT>>
```
You should see a JSON object containing the metrics information.

3. Run the Memgraph exporter
```shell
$ cd prometheus-exporter
$ python3 mg_exporter.py --type=standalone
```
4. Make sure the exporter is running
```shell
$ curl <<EXPORTER_HOST>>:<<EXPORTER_PORT>>
```
You should see a Prometheus object containing the metrics information.

5. Launch Prometheus
```shell
$ cd prometheus-exporter
$ docker run --name memgraph-prometheus -d -v $(pwd)/config:/etc/prometheus -p 9090:9090 prom/prometheus
```
6. Open the Prometheus UI by going to http://localhost:9090

## Grafana dashboard

To add the Memgraph Grafana dashboard to your Grafana instance, you can download the `kube_prometheus_stack_memgraph_dashboard.yaml` file and apply it to your Grafana instance using `helm upgrade` and pass it as a value file, or `helm install` when setting up the monitoring stack, e.g.
```bash
helm upgrade --install kube-prometheus-stack oci://ghcr.io/prometheus-community/charts/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  -f kube_prometheus_stack_memgraph_dashboard.yaml
```

### Updating the dashboard

If changes are made to the exporter metrics, the `tools/generate_grafana_dashboard.py` script can be used to update the `memgraph-grafana-dashboard.json` file. It scrapes the metrics listed in the `metrics/` directory and generates a Grafana dashboard JSON file. Then, the `tools/generate_kube_prometheus_stack_dashboard_values.py` script can be used to update the `kube_prometheus_stack_memgraph_dashboard.yaml` file.
