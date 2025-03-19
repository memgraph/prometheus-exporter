import argparse
import logging


logging.basicConfig(format="%(asctime)-15s [%(levelname)s]: %(message)s")
logger = logging.getLogger("prometheus_handler")
logger.setLevel(logging.INFO)


def main(deployment_type):
    if deployment_type == "standalone":
        logger.info("Running in standalone mode.")
        import standalone_main

        standalone_main.run()

    elif deployment_type == "HA":
        logger.info("Running in High Availability (HA) mode.")
        import ha_main

        ha_main.run()
    else:
        logger.error("Invalid deployment type. Please choose 'standalone' or 'HA'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process deployment type.")

    parser.add_argument(
        "--type",
        type=str,
        choices=["standalone", "HA"],
        default="standalone",
        required=True,
        help="Type of deployment: standalone or HA",
    )

    args = parser.parse_args()

    main(args.type)
