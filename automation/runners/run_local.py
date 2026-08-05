from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str, allow_failure: bool = False) -> int:
    completed = subprocess.run(args, cwd=ROOT, check=False)
    if completed.returncode and not allow_failure:
        raise SystemExit(completed.returncode)
    return completed.returncode


def main() -> None:
    run(sys.executable, "data/generate_test_catalog.py")
    test_exit = run(
        sys.executable,
        "-m",
        "pytest",
        "tests/test_enterprise_catalog.py",
        "--reruns",
        "2",
        "--reruns-delay",
        "1",
        "-v",
        allow_failure=True,
    )
    report_exit = run(
        sys.executable,
        "utils/report_generator.py",
        "--input",
        "Test Results",
        "--output",
        "Test Results",
        allow_failure=True,
    )
    raise SystemExit(report_exit or test_exit)


if __name__ == "__main__":
    main()

