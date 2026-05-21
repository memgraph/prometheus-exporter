import logging
import time
import requests
import urllib3
import yaml

from prometheus_client import start_http_server

from ha_model import update_metrics


logger = logging.getLogger("prometheus_handler")


class GeneralConfig:
    def __init__(self, port, pull_frequency_seconds):
        self.port = port
        self.pull_frequency_seconds = pull_frequency_seconds


class InstanceConfig:
    def __init__(self, name, url, port, type, skip_tls_verify=True, ca_file=None):
        self.name = name
        self.url = url
        self.port = port
        self.type = type
        self.skip_tls_verify = skip_tls_verify
        self.ca_file = ca_file
        if self.skip_tls_verify and self.ca_file:
            logger.warning(
                "Instance %s has both skip_tls_verify=true and ca_file set; "
                "skip_tls_verify takes precedence and ca_file is ignored.",
                self.name,
            )

    def __str__(self):
        return (
            f"InstanceConfig(name={self.name}, url={self.url}, port={self.port}, "
            f"skip_tls_verify={self.skip_tls_verify}, ca_file={self.ca_file})"
        )


class HAExporterConfig:
    def __init__(self, config, instances):
        self.config = config
        self.instances = instances


def load_yaml_config(filepath):
    with open(filepath, "r") as file:
        return yaml.safe_load(file)


def _verify_arg(instance):
    if instance.skip_tls_verify:
        return False
    if instance.ca_file:
        return instance.ca_file
    return True


def pull_metrics(instance):
    res = requests.get(
        f"{instance.url}:{instance.port}", verify=_verify_arg(instance)
    )

    if res.status_code != 200:
        raise Exception(
            f"Memgraph instance on {instance.url}:{instance.port} couldn't be reached."
        )

    return res.json()


def run(config_file):
    config = load_yaml_config(config_file)
    instances = [
        InstanceConfig(
            name=instance["name"],
            url=instance["url"],
            port=instance["port"],
            type=instance["type"],
            skip_tls_verify=instance.get("skip_tls_verify", True),
            ca_file=instance.get("ca_file"),
        )
        for instance in config.get("instances", [])
    ]
    if any(inst.skip_tls_verify for inst in instances):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    instances_str = "\n\t".join(str(instance) for instance in instances)
    logger.info(
        "HA exporter will use the following instances to collect metrics:\n\t%s",
        instances_str,
    )
    general_config = GeneralConfig(
        port=config.get("exporter", {}).get("port", 9115),
        pull_frequency_seconds=config.get("exporter", {}).get(
            "pull_frequency_seconds", 0
        ),
    )
    logger.info(
        "HA exporter will pull metrics every %ds", general_config.pull_frequency_seconds
    )
    logger.info("HA exporter is started on: localhost:%s\n\n", general_config.port)
    exporter = HAExporterConfig(instances=instances, config=general_config)

    start_http_server(exporter.config.port)

    while True:
        for instance in exporter.instances:
            try:
                instance_metrics = pull_metrics(instance)
                update_metrics(instance_metrics, instance)
                logger.info("Send update to Prometheus for instance %s", instance.name)
            except Exception as e:
                logger.error("Error occurred while updating metrics: %s", e)
            finally:
                time.sleep(exporter.config.pull_frequency_seconds)


if __name__ == "__main__":
    run("ha_config.yaml")
