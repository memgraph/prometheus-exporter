#!/usr/bin/env python3
"""Poll the prometheus-exporter and verify it scrapes every expected metric.

Compares the set of metric names exposed at the exporter's ``/metrics`` endpoint
against the metrics defined under ``metrics/`` for standalone mode. Exits 0 if
all expected names are present, otherwise prints the missing metric names and
exits 1.
"""

import argparse
import os
import sys
import time
import urllib.error
import urllib.request

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from metrics.general_metrics import general_data
from metrics.index_metrics import index_data
from metrics.operator_metrics import operator_data
from metrics.query_metrics import query_data
from metrics.query_type_metrics import query_type_data
from metrics.session_metrics import session_data
from metrics.snapshot_metrics import snapshot_data
from metrics.stream_metrics import stream_data
from metrics.transaction_metrics import txn_data
from metrics.trigger_metrics import trigger_data
from metrics.ttl_metrics import ttl_data


def expected_standalone_metrics():
    names = set()
    for entries in (
        general_data,
        index_data,
        query_data,
        query_type_data,
        session_data,
        snapshot_data,
        stream_data,
        txn_data,
        trigger_data,
        ttl_data,
    ):
        for name, _ in entries:
            names.add(name)
    for name in operator_data:
        names.add(name)
    return names


def fetch(url, timeout):
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def parse_metric_names(text):
    names = set()
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        token = line.split(" ", 1)[0]
        token = token.split("{", 1)[0]
        if token:
            names.add(token)
    return names


def wait_until_reachable(url, attempts, delay, timeout):
    last_err = None
    for i in range(1, attempts + 1):
        try:
            return fetch(url, timeout)
        except (urllib.error.URLError, ConnectionError, TimeoutError) as err:
            last_err = err
            print(f"[{i}/{attempts}] exporter not reachable yet: {err}", flush=True)
            time.sleep(delay)
    raise SystemExit(f"Exporter never became reachable at {url}: {last_err}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--url",
        default="http://localhost:9115/metrics",
        help="Prometheus exporter /metrics URL.",
    )
    parser.add_argument(
        "--attempts",
        type=int,
        default=60,
        help="Number of polling attempts before giving up.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Seconds between polling attempts.",
    )
    parser.add_argument(
        "--http-timeout",
        type=float,
        default=5.0,
        help="HTTP timeout for each fetch.",
    )
    args = parser.parse_args()

    expected = expected_standalone_metrics()
    print(f"Expecting {len(expected)} metrics from the standalone exporter.")
    print(f"Polling {args.url} (up to {args.attempts} attempts, {args.delay}s apart)")

    wait_until_reachable(args.url, args.attempts, args.delay, args.http_timeout)

    missing = expected
    for attempt in range(1, args.attempts + 1):
        try:
            text = fetch(args.url, args.http_timeout)
        except (urllib.error.URLError, ConnectionError, TimeoutError) as err:
            print(f"[{attempt}/{args.attempts}] fetch failed: {err}", flush=True)
            time.sleep(args.delay)
            continue

        scraped = parse_metric_names(text)
        missing = expected - scraped
        if not missing:
            print(f"All {len(expected)} expected metrics are exposed by the exporter.")
            return 0

        print(
            f"[{attempt}/{args.attempts}] {len(missing)} metric(s) still missing "
            f"({len(expected) - len(missing)}/{len(expected)} present)",
            flush=True,
        )
        time.sleep(args.delay)

    print("", flush=True)
    print(f"FAIL: {len(missing)} metric(s) missing from {args.url}:", flush=True)
    for name in sorted(missing):
        print(f"  - {name}", flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())
