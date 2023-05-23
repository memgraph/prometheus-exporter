import time
import requests
import yaml

from yaml.loader import SafeLoader

from prometheus_client import start_http_server

from model import update_metrics


class ConfigConstants:
    EXPORTER = "exporter"
    ENDPOINT_URL = "endpoint_url"
    GENERAL = "general"
    MEMGRAPH = "memgraph"
    PORT = "port"
    PULL_FREQUENCY_SECONDS = "pull_frequency_seconds"


class Config:
    def __init__(
        self,
        memgraph_endpoint_url: str,
        memgraph_port: int,
        exporter_port: int,
        pull_frequency_seconds: int,
    ) -> None:
        self._memgraph_endpoint_url = memgraph_endpoint_url
        self._memgraph_port = memgraph_port
        self._exporter_port = exporter_port
        self._pull_frequency_seconds = pull_frequency_seconds

    @classmethod
    def from_yaml_file(cls, file_name: str = "config.yaml") -> "Config":
        with open(file_name) as f:
            data = yaml.load(f, Loader=SafeLoader)
            return Config(
                data[ConfigConstants.MEMGRAPH][ConfigConstants.ENDPOINT_URL],
                data[ConfigConstants.MEMGRAPH][ConfigConstants.PORT],
                data[ConfigConstants.EXPORTER][ConfigConstants.PORT],
                data[ConfigConstants.GENERAL][ConfigConstants.PULL_FREQUENCY_SECONDS],
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

    @property
    def pull_frequency_seconds(self) -> int:
        return self._pull_frequency_seconds


config_singleton = None


def pull_metrics():
    # We first want to fetch metrics from the Memgraph's HTTP endpoint
    res = requests.get(
        f"{config_singleton.memgraph_endpoint_url}:{config_singleton.memgraph_port}"
    )

    print(f"Pulled metrics: status code {res.status_code}")
    if res.status_code != 200:
        raise Exception(
            f"Status code is not 200, but {res.status_code}, please check running services!"
        )

    json_data = res.json()

    update_metrics(json_data)


if __name__ == "__main__":
    # Parse the configuration for starting the service and retrieve data from correct endpoints
    config_singleton = Config.from_yaml_file()
    start_http_server(config_singleton.exporter_port)

    # Continuously fetch metrics
    while True:
        time.sleep(config_singleton.pull_frequency_seconds)
        try:
            pull_metrics()
        except Exception as e:
            print("Exception occurred while pulling Memgraph metrics!")
            print(e)
            exit(1)
