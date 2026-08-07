"""
Baseline / Load Test for Smart Furnace API
------------------------------------------
100 virtual users · 1 minute · reports RPS + response times

Usage:
  python baseline_load_test.py
  python baseline_load_test.py --users 100 --duration 60 --host http://127.0.0.1:5000
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable

import requests

MATERIAL_PAIRS = [
    ("Zinc", "Iron"),
    ("Iron", "Steel"),
    ("Copper", "Brass"),
    ("Aluminum", "Alumina"),
    ("Titanium", "Titanium"),
    ("Silicon", "Silica"),
    ("Nickel", "Nickel"),
    ("Carbon", "Graphite"),
]


@dataclass
class Stats:
    lock: threading.Lock = field(default_factory=threading.Lock)
    latencies_ms: list[float] = field(default_factory=list)
    by_endpoint: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))
    status_counts: dict[int, int] = field(default_factory=lambda: defaultdict(int))
    error_reasons: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    errors: int = 0
    stop_at: float = 0.0

    def record(
        self,
        endpoint: str,
        elapsed_ms: float,
        status: int | None,
        ok: bool,
        reason: str | None = None,
    ) -> None:
        with self.lock:
            self.latencies_ms.append(elapsed_ms)
            self.by_endpoint[endpoint].append(elapsed_ms)
            if status is not None:
                self.status_counts[status] += 1
            if not ok:
                self.errors += 1
                if reason:
                    self.error_reasons[reason] += 1


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


def hit_synthesis_check(session: requests.Session, host: str) -> tuple[str, int]:
    base, target = random.choice(MATERIAL_PAIRS)
    url = f"{host}/api/synthesis/check"
    resp = session.post(
        url,
        data=json.dumps({"base_material": base, "target_material": target}),
        timeout=30,
    )
    # 200 = feasible, 400 = not feasible — both are valid API answers
    return "POST /api/synthesis/check", resp.status_code


def hit_predict(session: requests.Session, host: str) -> tuple[str, int]:
    base, target = random.choice(MATERIAL_PAIRS)
    url = f"{host}/api/predict"
    # Omit user_id so load test does not flood prediction_history
    resp = session.post(
        url,
        data=json.dumps(
            {
                "base_material": base,
                "target_material": target,
                "target_phase": "synthesis",
            }
        ),
        timeout=30,
    )
    return "POST /api/predict", resp.status_code


def hit_history(session: requests.Session, host: str) -> tuple[str, int]:
    url = f"{host}/api/history/1"
    resp = session.get(url, timeout=30)
    return "GET /api/history/1", resp.status_code


def hit_logout(session: requests.Session, host: str) -> tuple[str, int]:
    url = f"{host}/api/logout"
    resp = session.post(url, data=json.dumps({"user_id": 1}), timeout=30)
    return "POST /api/logout", resp.status_code


# Weighted mix: prediction/synthesis dominate real traffic
TASKS: list[tuple[Callable, int]] = [
    (hit_synthesis_check, 40),
    (hit_predict, 40),
    (hit_history, 15),
    (hit_logout, 5),
]


def pick_task() -> Callable:
    weighted: list[Callable] = []
    for fn, weight in TASKS:
        weighted.extend([fn] * weight)
    return random.choice(weighted)


def virtual_user(user_id: int, host: str, stats: Stats) -> None:
    session = make_session()
    # Stagger start so all 100 don't fire in the same millisecond
    time.sleep((user_id % 100) * 0.01)

    while time.time() < stats.stop_at:
        task = pick_task()
        started = time.perf_counter()
        status: int | None = None
        ok = False
        endpoint = "unknown"
        reason: str | None = None
        try:
            endpoint, status = task(session, host)
            ok = status is not None and status < 500
            if not ok and status is not None:
                reason = f"HTTP {status}"
        except Exception as exc:
            ok = False
            reason = type(exc).__name__
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        stats.record(endpoint, elapsed_ms, status, ok, reason)


def percentile(sorted_vals: list[float], p: float) -> float:
    if not sorted_vals:
        return 0.0
    k = (len(sorted_vals) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return sorted_vals[f]
    return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)


def print_report(stats: Stats, users: int, duration_s: float) -> dict:
    total = len(stats.latencies_ms)
    rps = total / duration_s if duration_s > 0 else 0.0
    sorted_lat = sorted(stats.latencies_ms)
    summary = {
        "virtual_users": users,
        "duration_s": round(duration_s, 1),
        "total_requests": total,
        "errors": stats.errors,
        "rps": round(rps, 1),
        "avg_ms": round(statistics.mean(sorted_lat), 0) if sorted_lat else None,
        "min_ms": round(sorted_lat[0], 0) if sorted_lat else None,
        "max_ms": round(sorted_lat[-1], 0) if sorted_lat else None,
        "p50_ms": round(percentile(sorted_lat, 50), 0) if sorted_lat else None,
        "p95_ms": round(percentile(sorted_lat, 95), 0) if sorted_lat else None,
        "p99_ms": round(percentile(sorted_lat, 99), 0) if sorted_lat else None,
        "status_counts": dict(stats.status_counts),
        "error_reasons": dict(stats.error_reasons),
        "passed": stats.errors == 0 and total > 0,
    }

    print()
    print("=" * 60)
    print("  BASELINE / LOAD TEST RESULTS")
    print("=" * 60)
    print(f"  Virtual users     : {users}")
    print(f"  Duration          : {duration_s:.1f}s")
    print(f"  Total requests    : {total}")
    print(f"  Errors            : {stats.errors}")
    print()
    print("  Requests per second (RPS)")
    print(f"    {rps:.1f} req/sec")
    print()
    print("  Response Time")
    if sorted_lat:
        print(f"    Average : {statistics.mean(sorted_lat):.0f}ms")
        print(f"    Min     : {sorted_lat[0]:.0f}ms")
        print(f"    Max     : {sorted_lat[-1]:.0f}ms")
        print(f"    p50     : {percentile(sorted_lat, 50):.0f}ms")
        print(f"    p95     : {percentile(sorted_lat, 95):.0f}ms")
        print(f"    p99     : {percentile(sorted_lat, 99):.0f}ms")
    else:
        print("    (no successful timings recorded)")
    print()
    print("  HTTP status codes")
    for code, count in sorted(stats.status_counts.items()):
        print(f"    {code}: {count}")
    if stats.error_reasons:
        print()
        print("  Top error reasons")
        for reason, count in sorted(
            stats.error_reasons.items(), key=lambda x: x[1], reverse=True
        )[:8]:
            print(f"    {reason}: {count}")
    print()
    print("  Per-endpoint average")
    for endpoint, times in sorted(stats.by_endpoint.items()):
        print(f"    {endpoint}: {statistics.mean(times):.0f}ms  ({len(times)} reqs)")
    print("=" * 60)
    print(f"  RESULT: {'PASSED' if summary['passed'] else 'FAILED'}")
    print("=" * 60)
    print()
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Baseline load test (100 VU / 1 min)")
    parser.add_argument("--host", default="http://127.0.0.1:5000")
    parser.add_argument("--users", type=int, default=100)
    parser.add_argument("--duration", type=int, default=60, help="seconds")
    parser.add_argument(
        "--report",
        default="baseline_load_report.json",
        help="Write JSON summary for CI artifacts",
    )
    parser.add_argument(
        "--max-error-rate",
        type=float,
        default=0.0,
        help="Fail if error_rate exceeds this fraction (0.0 = zero errors)",
    )
    args = parser.parse_args()

    print(f"Starting baseline load test against {args.host}")
    print(f"  {args.users} virtual users for {args.duration}s ...")
    print("  (omit Ctrl+C unless you want to abort early)")

    # Quick connectivity check
    try:
        r = requests.post(
            f"{args.host}/api/logout",
            json={"user_id": 1},
            timeout=5,
        )
    except Exception as exc:
        print(f"  Preflight FAILED: {exc}")
        print("  Is the API running? (python app.py uses Waitress)")
        raise SystemExit(1)

    print(f"  Preflight OK (logout -> HTTP {r.status_code})")

    stats = Stats()
    stats.stop_at = time.time() + args.duration
    wall_start = time.perf_counter()

    threads = [
        threading.Thread(target=virtual_user, args=(i, args.host, stats), daemon=True)
        for i in range(args.users)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    wall_elapsed = time.perf_counter() - wall_start
    summary = print_report(stats, args.users, wall_elapsed)

    with open(args.report, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
    print(f"Wrote report: {args.report}")

    total = summary["total_requests"]
    error_rate = (summary["errors"] / total) if total else 1.0
    if total == 0 or error_rate > args.max_error_rate:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
