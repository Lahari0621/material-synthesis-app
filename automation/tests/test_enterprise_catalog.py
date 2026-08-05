from __future__ import annotations

import subprocess
import time

import pytest

from config import settings
from pages.smart_furnace_app import SmartFurnaceApp


def _logged_out(app: SmartFurnaceApp) -> None:
    if app.is_logged_in():
        app.logout()
    if app.has_text("REQUEST ACCESS", timeout=1):
        app.tap_text("Already authorized? Access Terminal here.")
    app.wait_for_login()


def execute_case(app: SmartFurnaceApp, case: dict) -> str:
    handler = case["handler"]
    data = case["test_data"]
    variant = int(data["variant"])

    if case.get("blocked_reason"):
        pytest.skip(f"BLOCKED: {case['blocked_reason']}")

    if handler == "login_screen":
        _logged_out(app)
        app.find_by_text("Scientist Authorization")
        app.find_by_identifier("login_email_field")
        app.find_by_identifier("login_password_field")
        return "Login branding and controls are visible"

    if handler == "invalid_login":
        _logged_out(app)
        email = (
            f"invalid-{variant}"
            if variant % 2
            else f"unknown{variant}@smartfurnace.test"
        )
        password = "" if variant % 3 == 0 else "wrong-password"
        app.type_identifier("login_email_field", email)
        if password:
            app.type_identifier("login_password_field", password)
        app.tap_identifier("login_submit_button")
        assert app.has_text("SMART FURNACE AI")
        return "Invalid credentials were rejected"

    if handler == "valid_login":
        _logged_out(app)
        app.login()
        assert app.is_logged_in()
        return "Valid login reached the authenticated shell"

    if handler == "logout":
        app.login()
        app.logout()
        return "Logout cleared the session and returned to login"

    if handler == "registration_screen":
        _logged_out(app)
        app.open_registration()
        app.find_by_identifier("register_name_field")
        app.find_by_identifier("register_email_field")
        app.find_by_identifier("register_password_field")
        return "Registration fields and action are visible"

    if handler == "registration_validation":
        _logged_out(app)
        app.open_registration()
        app.tap_identifier("register_submit_button")
        app.find_by_text("Scientist name is required.")
        return "Registration mandatory-field validation displayed"

    if handler == "profile_read_only":
        app.login()
        app.open_tab("Settings")
        app.find_by_text("User Profile")
        app.find_by_text(settings.TEST_EMAIL)
        return "Read-only user profile is displayed"

    if handler == "navigation":
        app.login()
        tab = SmartFurnaceApp.NAV_TABS[(variant - 1) % 4]
        app.open_tab(tab)
        return f"Navigation opened {tab}"

    if handler == "dashboard":
        app.login()
        app.open_tab("Dashboard")
        app.find_by_text("Synthesis Parameters")
        app.find_by_identifier("dashboard_base_material_field")
        app.find_by_identifier("dashboard_target_material_field")
        return "Dashboard parameters and controls are visible"

    if handler == "dashboard_validation":
        app.login()
        app.submit_empty_dashboard()
        return "Dashboard mandatory-field validation displayed"

    if handler == "synthesis":
        app.login()
        result = app.run_synthesis(
            data["base_material"], data["target_material"]
        )
        return f"Synthesis returned {result}"

    if handler == "form_presence":
        _logged_out(app)
        app.find_by_identifier("login_email_field")
        app.find_by_identifier("login_password_field")
        return "Form controls are discoverable"

    if handler == "form_entry":
        _logged_out(app)
        app.type_identifier(
            "login_email_field", f"form{variant}@smartfurnace.test"
        )
        app.type_identifier("login_password_field", f"FormPass{variant}!")
        return "Form accepted data-driven input"

    if handler == "history_read":
        app.login()
        app.open_tab("History")
        app.find_by_text("Experiment Records")
        app.wait_until_any_text(
            ["View Details", "No experiment history found", "Successful"], timeout=15
        )
        return "History records area loaded"

    if handler == "input_validation":
        if variant % 2:
            _logged_out(app)
            app.submit_empty_login()
            app.find_by_text("Please enter your email address.")
            return "Login validation displayed"
        app.login()
        app.submit_empty_dashboard()
        return "Dashboard validation displayed"

    if handler == "error_handling":
        _logged_out(app)
        app.type_identifier(
            "login_email_field", f"missing{variant}@smartfurnace.test"
        )
        app.type_identifier("login_password_field", "invalid-password")
        app.tap_identifier("login_submit_button")
        app.find_by_text("Invalid email or password")
        return "API authentication error displayed without crash"

    if handler == "session":
        app.login()
        app.restart()
        app.find_by_text("Home")
        return "Authenticated session survived app restart"

    if handler == "notifications":
        app.login()
        enabled = variant % 2 == 0
        app.set_notifications(enabled)
        return f"Notifications preference set to {enabled}"

    if handler == "offline":
        app.login()
        subprocess.run(
            [
                "adb", "-s", settings.UDID, "shell", "settings", "put",
                "global", "airplane_mode_on", "1",
            ],
            check=False,
        )
        subprocess.run(
            [
                "adb", "-s", settings.UDID, "shell", "am", "broadcast",
                "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true",
            ],
            check=False,
        )
        try:
            app.open_tab("Dashboard")
            app.type_identifier("dashboard_base_material_field", "Zinc")
            app.type_identifier("dashboard_target_material_field", "Iron")
            app.tap_identifier("dashboard_check_feasibility_button")
            app.wait_until_any_text(
                ["Failed to connect", "Feasibility review"], timeout=20
            )
        finally:
            subprocess.run(
                [
                    "adb", "-s", settings.UDID, "shell", "settings", "put",
                    "global", "airplane_mode_on", "0",
                ],
                check=False,
            )
            subprocess.run(
                [
                    "adb", "-s", settings.UDID, "shell", "am", "broadcast",
                    "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "false",
                ],
                check=False,
            )
        return "Offline request was handled without application crash"

    if handler == "accessibility":
        _logged_out(app)
        identifiers = (
            "login_email_field",
            "login_password_field",
            "login_submit_button",
            "login_register_link",
        )
        app.find_by_identifier(identifiers[(variant - 1) % len(identifiers)])
        return "Accessibility identifier is exposed to UiAutomator2"

    if handler == "responsive":
        app.login()
        orientation = "LANDSCAPE" if variant % 2 else "PORTRAIT"
        app.driver.orientation = orientation
        app.open_tab("Home")
        app.find_by_text("Welcome to Smart Furnace AI")
        app.driver.orientation = "PORTRAIT"
        return f"Layout remained usable in {orientation}"

    if handler == "performance":
        app.login()
        tab = SmartFurnaceApp.NAV_TABS[(variant - 1) % 4]
        elapsed = app.measure_navigation_ms(tab)
        assert elapsed <= settings.PERFORMANCE_LIMIT_MS, (
            f"{tab} navigation took {elapsed:.0f}ms; "
            f"limit is {settings.PERFORMANCE_LIMIT_MS}ms"
        )
        return f"{tab} navigation completed in {elapsed:.0f}ms"

    raise AssertionError(f"No executable handler for {handler}")


@pytest.mark.usefixtures("driver")
def test_enterprise_case(driver, test_case):
    started = time.perf_counter()
    actual = execute_case(SmartFurnaceApp(driver), test_case)
    test_case["actual_result"] = actual
    test_case["execution_time_ms"] = round(
        (time.perf_counter() - started) * 1000, 1
    )

