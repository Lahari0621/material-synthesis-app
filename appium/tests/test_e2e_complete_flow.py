"""Complete Android Appium end-to-end suite for Smart Furnace AI."""

from __future__ import annotations

import time

from config import settings
from pages.dashboard_page import DashboardPage
from pages.history_page import HistoryPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from pages.settings_page import SettingsPage


class TestAppiumEndToEnd:
    def test_01_login_screen_loads(self, driver, record):
        started = time.perf_counter()
        try:
            page = LoginPage(driver)
            page.assert_loaded()
            record("TC-01", "Auth", "Login screen loads with branding", "PASSED", started)
        except Exception as exc:
            record("TC-01", "Auth", "Login screen loads with branding", "FAILED", started, str(exc))
            raise

    def test_02_login_validation_empty_fields(self, driver, record):
        started = time.perf_counter()
        try:
            page = LoginPage(driver)
            page.submit()
            # Stay on login when credentials missing
            assert page.has_text("SMART FURNACE AI")
            record("TC-02", "Auth", "Login rejects empty credentials", "PASSED", started)
        except Exception as exc:
            record("TC-02", "Auth", "Login rejects empty credentials", "FAILED", started, str(exc))
            raise

    def test_03_navigate_to_register(self, driver, record):
        started = time.perf_counter()
        try:
            login = LoginPage(driver)
            login.go_to_register()
            RegisterPage(driver).assert_loaded()
            record("TC-03", "Auth", "Navigate login -> register", "PASSED", started)
        except Exception as exc:
            record("TC-03", "Auth", "Navigate login -> register", "FAILED", started, str(exc))
            raise

    def test_04_register_and_land_on_home(self, driver, record):
        started = time.perf_counter()
        try:
            login = LoginPage(driver)
            if login.has_text("ACCESS TERMINAL"):
                login.go_to_register()
            register = RegisterPage(driver)
            register.register(settings.TEST_NAME, settings.TEST_EMAIL, settings.TEST_PASSWORD)
            HomePage(driver).assert_loaded()
            record("TC-04", "Auth", "Register scientist and open Home", "PASSED", started)
        except Exception as exc:
            record("TC-04", "Auth", "Register scientist and open Home", "FAILED", started, str(exc))
            raise

    def test_05_login_success_flow(self, driver, record):
        started = time.perf_counter()
        try:
            login = LoginPage(driver)
            login.login(settings.TEST_EMAIL, settings.TEST_PASSWORD)
            HomePage(driver).assert_loaded()
            record("TC-05", "Auth", "Login success reaches Home", "PASSED", started)
        except Exception as exc:
            record("TC-05", "Auth", "Login success reaches Home", "FAILED", started, str(exc))
            raise

    def test_06_home_content(self, driver, record):
        started = time.perf_counter()
        try:
            LoginPage(driver).login(settings.TEST_EMAIL, settings.TEST_PASSWORD)
            home = HomePage(driver)
            home.assert_loaded()
            assert home.has_text("About Our Product")
            assert home.has_text("Key Features")
            record("TC-06", "Home", "Home content sections visible", "PASSED", started)
        except Exception as exc:
            record("TC-06", "Home", "Home content sections visible", "FAILED", started, str(exc))
            raise

    def test_07_open_dashboard(self, driver, record):
        started = time.perf_counter()
        try:
            LoginPage(driver).login(settings.TEST_EMAIL, settings.TEST_PASSWORD)
            HomePage(driver).open_tab("Dashboard")
            DashboardPage(driver).assert_loaded()
            record("TC-07", "Dashboard", "Open Synthesis Dashboard", "PASSED", started)
        except Exception as exc:
            record("TC-07", "Dashboard", "Open Synthesis Dashboard", "FAILED", started, str(exc))
            raise

    def test_08_dashboard_requires_materials(self, driver, record):
        started = time.perf_counter()
        try:
            LoginPage(driver).login(settings.TEST_EMAIL, settings.TEST_PASSWORD)
            HomePage(driver).open_tab("Dashboard")
            dash = DashboardPage(driver)
            dash.check_feasibility()
            assert dash.has_text("Base and Target materials are required.")
            record("TC-08", "Dashboard", "Validation for empty materials", "PASSED", started)
        except Exception as exc:
            record(
                "TC-08",
                "Dashboard",
                "Validation for empty materials",
                "FAILED",
                started,
                str(exc),
            )
            raise

    def test_09_dashboard_synthesis_check(self, driver, record):
        started = time.perf_counter()
        try:
            LoginPage(driver).login(settings.TEST_EMAIL, settings.TEST_PASSWORD)
            HomePage(driver).open_tab("Dashboard")
            dash = DashboardPage(driver)
            dash.run_synthesis("Zinc", "Iron")
            assert dash.has_text("Feasibility review") or dash.has_text("Target Temp:")
            record("TC-09", "Dashboard", "Run synthesis feasibility check", "PASSED", started)
        except Exception as exc:
            record(
                "TC-09",
                "Dashboard",
                "Run synthesis feasibility check",
                "FAILED",
                started,
                str(exc),
            )
            raise

    def test_10_history_screen(self, driver, record):
        started = time.perf_counter()
        try:
            LoginPage(driver).login(settings.TEST_EMAIL, settings.TEST_PASSWORD)
            HomePage(driver).open_tab("History")
            HistoryPage(driver).assert_loaded()
            record("TC-10", "History", "History screen loads", "PASSED", started)
        except Exception as exc:
            record("TC-10", "History", "History screen loads", "FAILED", started, str(exc))
            raise

    def test_11_settings_screen(self, driver, record):
        started = time.perf_counter()
        try:
            LoginPage(driver).login(settings.TEST_EMAIL, settings.TEST_PASSWORD)
            HomePage(driver).open_tab("Settings")
            SettingsPage(driver).assert_loaded()
            record("TC-11", "Settings", "Settings screen loads", "PASSED", started)
        except Exception as exc:
            record("TC-11", "Settings", "Settings screen loads", "FAILED", started, str(exc))
            raise

    def test_12_logout_returns_to_login(self, driver, record):
        started = time.perf_counter()
        try:
            LoginPage(driver).login(settings.TEST_EMAIL, settings.TEST_PASSWORD)
            HomePage(driver).open_tab("Settings")
            SettingsPage(driver).logout()
            LoginPage(driver).assert_loaded()
            record("TC-12", "Settings", "Logout returns to login", "PASSED", started)
        except Exception as exc:
            record("TC-12", "Settings", "Logout returns to login", "FAILED", started, str(exc))
            raise

    def test_13_full_end_to_end_journey(self, driver, record):
        started = time.perf_counter()
        try:
            login = LoginPage(driver)
            login.go_to_register()
            RegisterPage(driver).register(
                settings.TEST_NAME, settings.TEST_EMAIL, settings.TEST_PASSWORD
            )
            home = HomePage(driver)
            home.assert_loaded()
            home.open_tab("Dashboard")
            DashboardPage(driver).run_synthesis("Titanium", "Titanium")
            home.open_tab("History")
            HistoryPage(driver).assert_loaded()
            home.open_tab("Settings")
            SettingsPage(driver).logout()
            LoginPage(driver).assert_loaded()
            record(
                "TC-13",
                "E2E",
                "Complete register->dashboard->history->logout journey",
                "PASSED",
                started,
            )
        except Exception as exc:
            record(
                "TC-13",
                "E2E",
                "Complete register->dashboard->history->logout journey",
                "FAILED",
                started,
                str(exc),
            )
            raise
