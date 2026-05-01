#!/usr/bin/env python3
"""Poll the prometheus-exporter and verify it scrapes every expected metric.

Compares the set of metric names exposed at the exporter's ``/metrics`` endpoint
against the metrics defined under ``metrics/`` for standalone mode. Exits 0 if
all expected names are present, otherwise prints the missing metric names and
exits 1.

Optionally also waits for one or more required metrics to report a non-zero
value (proving the exporter is actually receiving data from Memgraph, not just
exposing default-zero gauges).
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


def parse_metric_values(text):
    """Return name -> max value across label combinations.

    Using max so a metric counts as "non-zero" if any sample has a positive
    value, which is the right semantics for things like memory_usage that have
    no labels but matters for any future labeled metrics too.
    """
    values = {}
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.rsplit(" ", 1)
        if len(parts) < 2:
            continue
        name = parts[0].split("{", 1)[0]
        try:
            value = float(parts[1])
        except ValueError:
            continue
        prev = values.get(name)
        if prev is None or value > prev:
            values[name] = value
    return values


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


def wait_for_names(url, expected, attempts, delay, http_timeout):
    missing = expected
    for attempt in range(1, attempts + 1):
        try:
            text = fetch(url, http_timeout)
            print("========= Response Data =========", flush=True)
            print(text, flush=True)
            print("================================", flush=True)
        except (urllib.error.URLError, ConnectionError, TimeoutError) as err:
            print(f"[{attempt}/{attempts}] fetch failed: {err}", flush=True)
            time.sleep(delay)
            continue

        scraped = parse_metric_names(text)
        missing = expected - scraped
        if not missing:
            print(f"All {len(expected)} expected metrics are exposed by the exporter.")
            return set()

        print(
            f"[{attempt}/{attempts}] {len(missing)} metric(s) still missing "
            f"({len(expected) - len(missing)}/{len(expected)} present)",
            flush=True,
        )
        time.sleep(delay)
    return missing


def wait_for_non_zero(url, names, timeout_seconds, delay, http_timeout):
    deadline = time.monotonic() + timeout_seconds
    print(
        f"Waiting up to {timeout_seconds:.0f}s for required metrics to become "
        f"non-zero: {names}",
        flush=True,
    )
    still_zero = list(names)
    while True:
        try:
            text = fetch(url, http_timeout)
        except (urllib.error.URLError, ConnectionError, TimeoutError) as err:
            print(f"fetch failed: {err}", flush=True)
            text = ""

        values = parse_metric_values(text)
        still_zero = [n for n in names if values.get(n, 0.0) <= 0.0]
        if not still_zero:
            for name in names:
                print(f"  {name} = {values.get(name)}", flush=True)
            print("All required metrics have non-zero values.", flush=True)
            return []

        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return still_zero

        present = [
            f"{n}={values.get(n, 0.0)}" for n in names if n not in still_zero
        ]
        print(
            f"still zero: {still_zero}; non-zero so far: {present}; "
            f"~{int(remaining)}s remaining",
            flush=True,
        )
        time.sleep(min(delay, max(remaining, 0.1)))


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
        help="Number of polling attempts during the metric-name check.",
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
    parser.add_argument(
        "--require-non-zero",
        action="append",
        default=[],
        metavar="METRIC",
        help=(
            "Require this metric to report a non-zero value before exiting "
            "successfully. May be repeated. Proves real data is flowing from "
            "Memgraph through the exporter, not just default gauges."
        ),
    )
    parser.add_argument(
        "--non-zero-timeout",
        type=float,
        default=180.0,
        help="Total seconds to wait for required metrics to become non-zero.",
    )
    args = parser.parse_args()

    expected = expected_standalone_metrics()
    print(f"Expecting {len(expected)} metrics from the standalone exporter.")
    print(f"Polling {args.url} (up to {args.attempts} attempts, {args.delay}s apart)")

    wait_until_reachable(args.url, args.attempts, args.delay, args.http_timeout)

    missing = wait_for_names(
        args.url, expected, args.attempts, args.delay, args.http_timeout
    )
    if missing:
        print("", flush=True)
        print(f"FAIL: {len(missing)} metric(s) missing from {args.url}:", flush=True)
        for name in sorted(missing):
            print(f"  - {name}", flush=True)
        return 1

    if args.require_non_zero:
        unknown = [n for n in args.require_non_zero if n not in expected]
        if unknown:
            print(
                f"FAIL: --require-non-zero references unknown metric(s): {unknown}",
                flush=True,
            )
            return 1
        still_zero = wait_for_non_zero(
            args.url,
            args.require_non_zero,
            args.non_zero_timeout,
            args.delay,
            args.http_timeout,
        )
        if still_zero:
            print("", flush=True)
            print(
                f"FAIL: required metric(s) never became non-zero "
                f"within {args.non_zero_timeout:.0f}s: {still_zero}",
                flush=True,
            )
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
