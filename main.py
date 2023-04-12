from prometheus_client import start_http_server, Summary, Counter, Gauge, Histogram
import random
import time
import requests

# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
SIZE_CTR = Counter('size_counter', 'Size counter description')
SIZE_GG = Gauge('size_gauge', 'Size gauge description')
HISTOGRAM = Histogram('histie', 'Histogram description')

@REQUEST_TIME.time()
def pull_metrics():
    """ Pull Memgraph metrics """
    res = requests.get("http://localhost:9092/")
    if res.status_code != 200:
        raise Exception("Status code is not 200!")
    
    json_data = res.json()
    size = json_data["size"]
    SIZE_CTR.inc(size)
    SIZE_GG.set(size)
    HISTOGRAM.observe(random.random())


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    # Generate some requests.
    while True:
        time.sleep(5)
        pull_metrics()
