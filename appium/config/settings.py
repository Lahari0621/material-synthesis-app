import os
from pathlib import Path

APPIUM_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APPIUM_ROOT.parent
REPORTS_DIR = APPIUM_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

APP_PACKAGE = os.getenv("APP_PACKAGE", "com.example.ai_smart_furncae_change")
APP_ACTIVITY = os.getenv(
    "APP_ACTIVITY",
    "com.example.ai_smart_furncae_change.MainActivity",
)
APK_PATH = os.getenv(
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

APPIUM_SERVER_URL = os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723")
# appium = real device/emulator, simulated = CI-safe flow driver
E2E_DRIVER = os.getenv("E2E_DRIVER", "simulated").lower()

IMPLICIT_WAIT_SEC = int(os.getenv("IMPLICIT_WAIT_SEC", "8"))
EXPLICIT_WAIT_SEC = int(os.getenv("EXPLICIT_WAIT_SEC", "20"))

TEST_EMAIL = os.getenv("E2E_EMAIL", "scientist@smartfurnace.test")
TEST_PASSWORD = os.getenv("E2E_PASSWORD", "Passw0rd!")
TEST_NAME = os.getenv("E2E_NAME", "Baseline Scientist")

EXCEL_REPORT_NAME = os.getenv(
    "EXCEL_REPORT_NAME", "Appium_E2E_Excel_Analysis_Report.xlsx"
)
