from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

import pytest

from config import settings
from drivers.android_driver import create_android_driver


CATALOG_PATH = settings.ROOT / "data" / "test_cases.json"
RESULTS: dict[str, dict] = {}
SESSION_STARTED = time.time()


def _load_shard() -> list[dict]:
    cases = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    selected = [
        case
        for index, case in enumerate(cases)
        if index % settings.SHARD_TOTAL == settings.SHARD_INDEX
    ]
    if not selected:
        raise RuntimeError(
            f"Shard {settings.SHARD_INDEX}/{settings.SHARD_TOTAL} has no cases"
        )
    return selected


def pytest_generate_tests(metafunc):
    if "test_case" not in metafunc.fixturenames:
        return
    params = []
    for case in _load_shard():
        marks = []
        if case["priority"] == "Critical":
            marks.append(pytest.mark.critical)
        elif case["priority"] == "High":
            marks.append(pytest.mark.high)
        if case["module"] == "Regression Suite":
            marks.append(pytest.mark.regression)
        if case.get("blocked_reason"):
            marks.append(pytest.mark.blocked)
        params.append(pytest.param(case, id=case["test_id"], marks=marks))
    metafunc.parametrize("test_case", params)


@pytest.fixture(scope="session")
def driver():
    mobile_driver = create_android_driver()
    yield mobile_driver
    try:
        mobile_driver.quit()
    except Exception:
        pass


def _capture_failure(driver, test_id: str) -> tuple[str, str]:
    screenshot_dir = settings.RESULTS_ROOT / "Screenshots"
    log_dir = settings.RESULTS_ROOT / "Logs"
    screenshot = screenshot_dir / f"{test_id}.png"
    device_log = log_dir / f"{test_id}-logcat.txt"

    try:
        driver.save_screenshot(str(screenshot))
    except Exception as exc:
        screenshot.write_text(f"Screenshot capture failed: {exc}", encoding="utf-8")

    try:
        result = subprocess.run(
            ["adb", "-s", settings.UDID, "logcat", "-d", "-t", "1500"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        device_log.write_text(
            result.stdout + "\n" + result.stderr, encoding="utf-8"
        )
    except Exception as exc:
        device_log.write_text(f"Logcat capture failed: {exc}", encoding="utf-8")

    return str(screenshot), str(device_log)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or "test_case" not in item.funcargs:
        return

    case = dict(item.funcargs["test_case"])
    status = "PASSED"
    actual = case.get("actual_result") or case["expected_result"]
    failure_reason = ""
    screenshot = ""
    device_log = ""

    if report.outcome == "rerun":
        return
    if report.failed:
        status = "FAILED"
        failure_reason = str(report.longrepr)
        actual = failure_reason
        if "driver" in item.funcargs:
            screenshot, device_log = _capture_failure(
                item.funcargs["driver"], case["test_id"]
            )
    elif report.skipped:
        text = str(report.longrepr)
        if "BLOCKED:" in text or case.get("blocked_reason"):
            status = "BLOCKED"
            failure_reason = case.get("blocked_reason") or text
        else:
            status = "SKIPPED"
            failure_reason = text
        actual = failure_reason

    case.update(
        {
            "status": status,
            "actual_result": actual,
            "failure_reason": failure_reason,
            "execution_time_ms": round(report.duration * 1000, 1),
            "screenshot": screenshot,
            "device_log": device_log,
            "shard": settings.SHARD_INDEX,
        }
    )
    RESULTS[case["test_id"]] = case


def pytest_sessionfinish(session, exitstatus):
    if not RESULTS:
        return
    output = (
        settings.RESULTS_ROOT
        / "JSON"
        / f"shard-{settings.SHARD_INDEX}-results.json"
    )
    payload = {
        "metadata": {
            "build_number": settings.BUILD_NUMBER,
            "git_commit": settings.COMMIT_SHA,
            "branch": settings.BRANCH,
            "device": settings.DEVICE_NAME,
            "android_version": settings.PLATFORM_VERSION,
            "shard_index": settings.SHARD_INDEX,
            "shard_total": settings.SHARD_TOTAL,
            "duration_seconds": round(time.time() - SESSION_STARTED, 2),
            "pytest_exit_status": int(exitstatus),
        },
        "results": sorted(RESULTS.values(), key=lambda row: row["test_id"]),
    }
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nShard JSON report: {output}")

