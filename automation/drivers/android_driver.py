from __future__ import annotations

from appium import webdriver
from appium.options.android import UiAutomator2Options

from config import settings


def create_android_driver():
    """Create a real UiAutomator2 session. No simulated fallback is allowed."""
    if not settings.APK_PATH.exists():
        raise FileNotFoundError(f"APK not found: {settings.APK_PATH}")

    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = settings.DEVICE_NAME
    options.udid = settings.UDID
    options.platform_version = settings.PLATFORM_VERSION
    options.app = str(settings.APK_PATH)
    options.app_package = settings.APP_PACKAGE
    options.app_activity = settings.APP_ACTIVITY
    options.no_reset = False
    options.full_reset = False
    options.auto_grant_permissions = True
    options.new_command_timeout = settings.COMMAND_TIMEOUT
    options.set_capability("appium:ensureWebviewsHavePages", True)
    options.set_capability("appium:disableWindowAnimation", True)

    driver = webdriver.Remote(settings.APPIUM_URL, options=options)
    driver.implicitly_wait(2)
    return driver

