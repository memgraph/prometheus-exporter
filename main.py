import logging
import time
import requests
import yaml

from yaml.loader import SafeLoader

from prometheus_client import start_http_server

from model import update_metrics


logging.basicConfig(format="%(asctime)-15s [%(levelname)s]: %(message)s")
logger = logging.getLogger("prometheus_handler")
logger.setLevel(logging.INFO)


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


def pull_metrics(config: Config):
    res = requests.get(f"{config.memgraph_endpoint_url}:{config.memgraph_port}")

    if res.status_code != 200:
        raise Exception(
            f"Status code is not 200, but {res.status_code}, please check running services!"
        )

    json_data = res.json()

    update_metrics(json_data)
    logger.info(f"Sent update to Prometheus")


if __name__ == "__main__":
    # Parse the configuration for starting the service and retrieve data from correct endpoints
    config = Config.from_yaml_file()
    start_http_server(config.exporter_port)

    # Continuously fetch metrics
    while True:
        try:
            time.sleep(config.pull_frequency_seconds)
            pull_metrics(config)
        except Exception as e:
            logger.error("Error occurred while updating metrics: {}", e)
