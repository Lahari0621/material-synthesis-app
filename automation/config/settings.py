from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parent
RESULTS_ROOT = ROOT / "Test Results"

APPIUM_URL = os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723")
APP_PACKAGE = os.getenv(
    "APP_PACKAGE", "com.example.ai_smart_furncae_change"
)
APP_ACTIVITY = os.getenv(
    "APP_ACTIVITY", "com.example.ai_smart_furncae_change.MainActivity"
)
APK_PATH = Path(
    os.getenv(
        "APK_PATH",
        str(
            PROJECT_ROOT
            / "build"
            / "app"
            / "outputs"
            / "flutter-apk"
            / "app-debug.apk"
        ),
    )
)
DEVICE_NAME = os.getenv("DEVICE_NAME", "Android Emulator")
UDID = os.getenv("ANDROID_UDID", "emulator-5554")
PLATFORM_VERSION = os.getenv("ANDROID_VERSION", "35")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0+1")

SHARD_INDEX = int(os.getenv("TEST_SHARD_INDEX", "0"))
SHARD_TOTAL = int(os.getenv("TEST_SHARD_TOTAL", "1"))
BUILD_NUMBER = os.getenv("GITHUB_RUN_NUMBER", "local")
COMMIT_SHA = os.getenv("GITHUB_SHA", "local")
BRANCH = os.getenv("GITHUB_REF_NAME", "local")

TEST_EMAIL = os.getenv("E2E_EMAIL", "scientist@smartfurnace.test")
TEST_PASSWORD = os.getenv("E2E_PASSWORD", "Passw0rd!")
TEST_NAME = os.getenv("E2E_NAME", "Automation Scientist")

WAIT_SECONDS = int(os.getenv("WAIT_SECONDS", "20"))
COMMAND_TIMEOUT = int(os.getenv("NEW_COMMAND_TIMEOUT", "240"))
PERFORMANCE_LIMIT_MS = int(os.getenv("PERFORMANCE_LIMIT_MS", "5000"))
CRITICAL_FAILURE_THRESHOLD = float(
    os.getenv("CRITICAL_FAILURE_THRESHOLD", "0.05")
)

for folder in (
    RESULTS_ROOT / "Excel",
    RESULTS_ROOT / "HTML",
    RESULTS_ROOT / "JSON",
    RESULTS_ROOT / "Screenshots",
    RESULTS_ROOT / "Logs",
    RESULTS_ROOT / "Summary",
    ROOT / "reports",
    ROOT / "screenshots",
    ROOT / "logs",
):
    folder.mkdir(parents=True, exist_ok=True)

