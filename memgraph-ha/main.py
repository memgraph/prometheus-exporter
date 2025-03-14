import logging
import time
import requests
import yaml

from prometheus_client import start_http_server

from model import update_metrics

logging.basicConfig(format="%(asctime)-15s [%(levelname)s]: %(message)s")
logger = logging.getLogger("prometheus_handler")
logger.setLevel(logging.INFO)


class GeneralConfig:
    def __init__(self, port, pull_frequency_seconds):
        self.port = port
        self.pull_frequency_seconds = pull_frequency_seconds


class InstanceConfig:
    def __init__(self, name, url, port, type):
        self.name = name
        self.url = url
        self.port = port
        self.type = type

    def __str__(self):
        return f"InstanceConfig(name={self.name}, url={self.url}, port={self.port})"


class HAExporterConfig:
    def __init__(self, config, instances):
        self.config = config
        self.instances = instances


def load_yaml_config(filepath):
    with open(filepath, "r") as file:
        return yaml.safe_load(file)


def pull_metrics(instance):
    res = requests.get(f"{instance.url}:{instance.port}")

    if res.status_code != 200:
        raise Exception(f"Memgraph instance on {instance.url}:{instance.port} couldn't be reached.")

    return res.json()


if __name__ == "__main__":
    config = load_yaml_config("config.yaml")
    instances = [InstanceConfig(name=instance['name'], url=instance['url'], port=instance['port'], type=instance["type"]) for instance in config.get('instances', [])]
    instances_str = '\n\t'.join(str(instance) for instance in instances)
    logger.info("HA exporter will use the following instances to collect metrics:\n\t%s", instances_str)
    general_config = GeneralConfig(port=config.get('exporter', {}).get('port', 9115), pull_frequency_seconds=config.get('exporter', {}).get('pull_frequency_seconds', 0))
    logger.info("HA exporter will pull metrics every %ds", general_config.pull_frequency_seconds)
    logger.info("HA exporter is started on: localhost:%s\n\n", general_config.port)
    exporter = HAExporterConfig(instances=instances, config=general_config)

    start_http_server(exporter.config.port)

    while True:
        for instance in exporter.instances:
            try:
                instance_metrics = pull_metrics(instance)
                logger.info("%s metrics:\n%s", instance.name, instance_metrics)
                update_metrics(instance_metrics, instance)
                logger.info("Send update to Prometheus for instance %s", instance.name)
            except Exception as e:
                logger.error("Error occurred while updating metrics: %s", e)
            finally:
                time.sleep(exporter.config.pull_frequency_seconds)
