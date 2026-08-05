from __future__ import annotations

import json
import os
from pathlib import Path

from config import settings


results_file = settings.RESULTS_ROOT / "JSON" / "execution-results.json"
payload = json.loads(results_file.read_text(encoding="utf-8"))
metrics = payload["metrics"]
results = payload["results"]
summary = settings.RESULTS_ROOT / "Summary" / "summary.md"

compact = [
    "# Android Appium E2E Execution Summary",
    "",
    f"- Build Number: {settings.BUILD_NUMBER}",
    f"- Git Commit: `{settings.COMMIT_SHA[:8]}`",
    f"- Branch: `{settings.BRANCH}`",
    f"- Device: {settings.DEVICE_NAME}",
    f"- Android Version: {settings.PLATFORM_VERSION}",
    "",
    "| Metric | Result |",
    "|---|---:|",
    f"| Total Test Cases | {metrics['total']} |",
    f"| Executed | {metrics['executed']} |",
    f"| Passed | {metrics['passed']} |",
    f"| Failed | {metrics['failed']} |",
    f"| Skipped | {metrics['skipped']} |",
    f"| Blocked | {metrics['blocked']} |",
    f"| Pass Percentage | {metrics['pass_percentage']}% |",
    f"| Fail Percentage | {metrics['fail_percentage']}% |",
    f"| Duration | {metrics['duration_seconds']}s |",
    "",
    "## Failed Critical/High Tests",
]
important_failures = [
    row for row in results
    if row["status"] == "FAILED" and row["priority"] in ("Critical", "High")
]
if important_failures:
    compact.extend(
        f"- ✗ `{row['test_id']}` {row['test_name']}: "
        f"{row.get('failure_reason', '')[:250]}"
        for row in important_failures
    )
else:
    compact.append("- None")

text = "\n".join(compact) + "\n"
summary.write_text(
    summary.read_text(encoding="utf-8") + "\n\n" + text,
    encoding="utf-8",
)
github_summary = os.getenv("GITHUB_STEP_SUMMARY")
if github_summary:
    with open(github_summary, "a", encoding="utf-8") as handle:
        handle.write(text)
else:
    print(text)

