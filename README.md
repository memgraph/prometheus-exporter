# Memgraph metrics exporter

[Memgraph](https://github.com/memgraph/memgraph) exporter for Prometheus.

The metrics currently collected are:

- **TODO**

## Running the exporter

```shell
$ git clone https://github.com/memgraph/prometheus-exporter.git
$ cd prometheus-exporter
$ python3 main.py
```

## Basic Prometheus Configuration

Add Memgraph target to the Prometheus `scrape_configs`:

```yaml
scrape_configs:
  - job_name: 'memgraph-metrics'
  static_configs:
    - targets: ['<<MEMGRAPH_EXPORTER_HOST>>:8000']
```
Adjust the host accordingly.

_A simple Prometheus configuration [prometheus.yml](config/prometheus.yml)._

## Running and Debugging the Setup

1. Startup your local Memgraph instance.
2. Make sure Memgraph is sending the metric information
```shell
$ curl localhost:9092
```
You should see a JSON object containing the metrics information.

3. Run the Memgraph exporter
```shell
$ cd prometheus-exporter
$ python3 main.py
```
4. Make sure the exporter is running
```shell
$ curl localhost:8000
```
You should see a Prometheus object containing the metrics information.
5. Launch Prometheus
```shell
$ docker run -d -v ./config:/etc/prometheus -p 9090:9090 prom/prometheus
```
6. Open the Prometheus UI by going to http://localhost:9090
7. Launch Grafana
```shell
$ docker run -d -p 3000:3000 grafana/grafana-enterprise
```
8. Open the Grafana UI by going to http://localhost:3000
9. Load our basic Grafana setup **TODO**
