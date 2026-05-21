from metrics._timer_helpers import generate_timer_metrics


memory_data = (
    [
        ("UnreleasedDeltaObjects", "Total number of unreleased delta objects in memory."),
        ("PeakMemoryRes", "Peak resident memory in the system."),
    ]
    + generate_timer_metrics("GCLatency", "GC execution latency in microseconds")
    + generate_timer_metrics("GCSkiplistCleanupLatency", "GC skiplist cleanup latency in microseconds")
)
