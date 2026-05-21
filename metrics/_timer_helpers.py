_percentiles = [50, 90, 99]


def generate_timer_metrics(metric, label=None):
    description = label if label is not None else f"{metric} latency in microseconds"
    return [
        (
            f"{metric}_us_{percentile}p",
            f"{description}, {percentile}th percentile",
        )
        for percentile in _percentiles
    ]
