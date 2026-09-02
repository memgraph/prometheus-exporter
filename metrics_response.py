import logging

logger = logging.getLogger("prometheus_handler")


def parse_json_metrics(res, endpoint):
    """Parse a Memgraph metrics response as JSON, with a clear error on OpenMetrics text."""
    try:
        return res.json()
    except ValueError as e:
        content_type = res.headers.get("Content-Type", "unknown")
        body = (res.text or "").lstrip()
        if (
            body.startswith("#")
            or "openmetrics" in content_type
            or "text/plain" in content_type
        ):
            raise ValueError(
                f"Memgraph at {endpoint} returned Prometheus/OpenMetrics text "
                f"(Content-Type: {content_type}), but this exporter requires JSON. "
                f"Remove '--metrics-format=OpenMetrics' from the Memgraph configuration "
                f"so it serves the default JSON metrics."
            ) from e
        snippet = body[:80].replace("\n", " ")
        raise ValueError(
            f"Memgraph at {endpoint} returned a non-JSON metrics response "
            f"(Content-Type: {content_type}): {snippet!r}"
        ) from e
