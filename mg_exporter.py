import logging
import os


logging.basicConfig(format="%(asctime)-15s [%(levelname)s]: %(message)s")
logger = logging.getLogger("prometheus_handler")
logger.setLevel(logging.INFO)


def main(deployment_type, config_file):
    if deployment_type == "standalone":
        logger.info("Running in standalone mode.")
        import standalone_main

        standalone_main.run(config_file)

    elif deployment_type == "HA":
        logger.info("Running in High Availability (HA) mode.")
        import ha_main

        ha_main.run(config_file)
    else:
        raise SystemExit(
            f"Invalid DEPLOYMENT_TYPE={deployment_type!r}; "
            "expected 'standalone' or 'HA'."
        )


if __name__ == "__main__":
    main(
        os.environ.get("DEPLOYMENT_TYPE", "standalone"),
        os.environ.get("CONFIG_FILE", "standalone_config.yaml"),
    )
