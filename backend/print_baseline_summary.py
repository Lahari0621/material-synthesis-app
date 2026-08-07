"""Pretty-print baseline_load_report.json for CI logs."""

import json
from pathlib import Path


def main() -> None:
    path = Path("baseline_load_report.json")
    if not path.exists():
        print("No report file found")
        return

    data = json.loads(path.read_text(encoding="utf-8"))
    print("=== Baseline Load Test Summary ===")
    for key in [
        "passed",
        "virtual_users",
        "duration_s",
        "total_requests",
        "errors",
        "rps",
        "avg_ms",
        "min_ms",
        "max_ms",
        "p95_ms",
    ]:
        print(f"{key}: {data.get(key)}")
    print("RESULT:", "PASSED" if data.get("passed") else "FAILED")


if __name__ == "__main__":
    main()
