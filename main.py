import time
import requests
import yaml

from yaml.loader import SafeLoader

from prometheus_client import start_http_server

from model import update_metrics


class ConfigConstants:
    EXPORTER = "exporter"
    HOST = "host"
    MEMGRAPH = "memgraph"
    PORT = "post"


class Config:
    def __init__(
        self, memgraph_endpoint_url: str, memgraph_port: int, exporter_port: int
    ) -> None:
        self._memgraph_endpoint_url = memgraph_endpoint_url
        self._memgraph_port = memgraph_port
        self._exporter_port = exporter_port

    @classmethod
    def from_yaml_file(cls, file_name: str = "config.yaml") -> "Config":
        with open(file_name) as f:
            data = yaml.load(f, Loader=SafeLoader)
            return Config(
                data[ConfigConstants.MEMGRAPH][ConfigConstants.HOST],
                data[ConfigConstants.MEMGRAPH][ConfigConstants.PORT],
                data[ConfigConstants.EXPORTER][ConfigConstants.PORT],
            )

    @property
    def exporter_port(self) -> int:
        return self._exporter_port

    @property
    def memgraph_endpoint_url(self) -> str:
        return self._memgraph_endpoint_url

    @property
    def memgraph_port(self) -> int:
        return self._memgraph_port


config_singleton = None


def pull_metrics():
    """Pull Memgraph metrics"""
    res = requests.get(
        f"{config_singleton.memgraph_endpoint_url}:{config_singleton.memgraph_port}"
    )
    if res.status_code != 200:
        raise Exception("Status code is not 200!")

    json_data = res.json()

    update_metrics(json_data)


if __name__ == "__main__":
    config_singleton = Config.from_yaml_file()
    # Start up the server to expose the metrics.
    start_http_server(config_singleton.exporter_port)
    # Generate some requests.
    while True:
        time.sleep(1)
        pull_metrics()
