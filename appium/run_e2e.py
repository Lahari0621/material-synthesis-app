"""Run Appium E2E suite and ensure Excel analysis report is produced."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(description="Smart Furnace Appium E2E runner")
    parser.add_argument(
        "--driver",
        choices=["simulated", "appium"],
        default=os.getenv("E2E_DRIVER", "simulated"),
    )
    args = parser.parse_args()
    os.environ["E2E_DRIVER"] = args.driver

    print(f"Running Appium E2E with driver mode: {args.driver}")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-v", "--tb=short"],
        cwd=str(ROOT),
        check=False,
    )
    report = ROOT / "reports" / "Appium_E2E_Excel_Analysis_Report.xlsx"
    if report.exists():
        print(f"Excel analysis report: {report}")
    else:
        print("WARNING: Excel report was not generated")
        return 1 if result.returncode == 0 else result.returncode
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
