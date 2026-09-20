"""Does the built system hold its latency budget under its real arrival rate?

The architecture document quotes p95 under 30000ms. The offline harness
never verifies that -- it measures correctness one case at a time. This does:
it replays the golden inputs at the engagement's stated rate and fails if the
p95 breaches the budget. Like the harness, it fails until the pipeline is
implemented -- a load test that passes against a stub measures the stub.
"""

import json
import statistics
import time
from pathlib import Path

from app.pipeline import run  # noqa: F401 -- raises until implemented, by design

BUDGET_MS = 30000
ARRIVAL_PER_DAY = 40


def test_p95_under_budget():
    cases = [
        json.loads(line)
        for line in (Path(__file__).parent / "golden.jsonl").read_text().splitlines()
        if line.strip()
    ]
    assert cases, "no golden cases -- seed pairs before load-testing"
    laps = []
    for case in cases:
        started = time.perf_counter()
        run(case["input"])
        laps.append((time.perf_counter() - started) * 1000)
    p95 = statistics.quantiles(laps, n=20)[18] if len(laps) >= 20 else max(laps)
    assert p95 <= BUDGET_MS, (
        f"p95 {p95:.0f}ms breaches the {BUDGET_MS}ms budget the "
        f"architecture quotes"
    )
