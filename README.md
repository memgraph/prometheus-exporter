# Memgraph metrics exporter

[Memgraph](https://github.com/memgraph/memgraph) exporter for Prometheus.

The metrics currently collected can be found [in the documentation](https://memgraph.com/docs/memgraph/next/reference-guide/exposing-system-metrics#system-metrics).

## Running the exporter

```shell
$ git clone https://github.com/memgraph/prometheus-exporter.git
$ cd prometheus-exporter
$ python3 -m pip install requests prometheus_client
$ python3 main.py
```

## Basic Prometheus Configuration

Add Memgraph target to the Prometheus `scrape_configs`:

```yaml
scrape_configs:
  - job_name: 'memgraph-metrics'
  static_configs:
    - targets: ['<<EXPORTER_HOST>>:<<EXPORTER_PORT>>']
```
Adjust the host accordingly.

_When running our basic setup as described bellow, the Prometheus configuration is already setup for you._

_For more informatioin about the Prometheus [scrape_configs](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#scrape_config)._

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
$ python3 main.py
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
7. Launch Grafana
```shell
$ docker run --name memgraph-grafana -d -p 3000:3000 grafana/grafana-enterprise
```
8. Open the Grafana UI by going to http://localhost:3000
9. Load our basic Grafana setup **TODO**
