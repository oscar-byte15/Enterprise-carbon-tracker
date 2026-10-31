
"""
Performance Benchmark - Calculation Engine

Subsystem 2: Carbon Activity Management

NFR2:
    Carbon emission calculations should complete
    in less than 50 milliseconds.

Notes:
    - Measures the real calculation function.
    - Includes emission factor JSON loading.
    - Does not include HTTP or database latency.
    - Benchmark results depend on the test environment.
"""

from statistics import mean
from time import perf_counter

from app.activities.calculator import calculate_emissions


MAX_TIME_MS = 50
ITERATIONS = 1000

TEST_CASES = [
    ("electricity", "Grid electricity", 500, "kWh"),
    ("heating", "Natural gas", 500, "kWh"),
    ("transport", "Petrol", 50, "L"),
    ("transport", "Diesel", 50, "L"),
    ("waste", "Plastic - Recycling", 100, "kg"),
    ("waste", "Organic - Composting", 100, "kg"),
    ("waste", "General - Landfill", 100, "kg"),
]


def run_benchmark():
    """
    Measure calculation latency across all supported
    activity types.

    Report average, 95th percentile, and maximum time.
    """

    durations = []

    # Warm up the Python interpreter and filesystem.
    for _ in range(20):
        for activity in TEST_CASES:
            calculate_emissions(*activity)

    # Measure individual calculations.
    for _ in range(ITERATIONS):
        for activity in TEST_CASES:

            start = perf_counter()

            calculate_emissions(*activity)

            end = perf_counter()

            elapsed_ms = (end - start) * 1000
            durations.append(elapsed_ms)

    durations.sort()

    average_ms = mean(durations)
    maximum_ms = max(durations)
    p95_index = int(0.95 * (len(durations) - 1))
    p95_ms = durations[p95_index]

    print("\n=== SUBSYSTEM 2 PERFORMANCE BENCHMARK ===")
    print(f"Calculations: {len(durations)}")
    print(f"Average latency: {average_ms:.4f} ms")
    print(f"P95 latency:     {p95_ms:.4f} ms")
    print(f"Maximum latency: {maximum_ms:.4f} ms")
    print(f"Target:          < {MAX_TIME_MS} ms")

    passed = maximum_ms < MAX_TIME_MS

    print(
        f"NFR2 result: {'PASS' if passed else 'FAIL'}"
    )

    return passed


if __name__ == "__main__":
    if not run_benchmark():
        raise SystemExit(1)
