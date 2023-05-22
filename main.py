import time
import requests

from prometheus_client import start_http_server

from model import update_metrics


def pull_metrics():
    """Pull Memgraph metrics"""
    res = requests.get("http://localhost:9092/")
    if res.status_code != 200:
        raise Exception("Status code is not 200!")

    json_data = res.json()

    update_metrics(json_data)


if __name__ == "__main__":
    # Start up the server to expose the metrics.
    start_http_server(8000)
    # Generate some requests.
    while True:
        time.sleep(1)
        pull_metrics()
