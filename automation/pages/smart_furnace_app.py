from __future__ import annotations

import time

from config import settings
from pages.base_page import BasePage


class SmartFurnaceApp(BasePage):
    NAV_TABS = ("Home", "Dashboard", "History", "Settings")

    def wait_for_login(self) -> None:
        self.find_by_text("SMART FURNACE AI")

    def is_logged_in(self) -> bool:
        return any(self.has_text(tab, timeout=1) for tab in self.NAV_TABS)

    def restart(self) -> None:
        self.driver.terminate_app(settings.APP_PACKAGE)
        self.driver.activate_app(settings.APP_PACKAGE)

    def reset(self) -> None:
        self.driver.execute_script(
            "mobile: clearApp",
            {"appId": settings.APP_PACKAGE},
        )
        self.driver.activate_app(settings.APP_PACKAGE)
        self.wait_for_login()

    def login(
        self,
        email: str = settings.TEST_EMAIL,
        password: str = settings.TEST_PASSWORD,
    ) -> None:
        if self.has_text("Synthesis Telemetry", timeout=1):
            self.driver.back()
        if self.is_logged_in():
            return
        if self.has_text("REQUEST ACCESS", timeout=1):
            self.tap_text("Already authorized? Access Terminal here.")
        self.wait_for_login()
        self.type_identifier("login_email_field", email)
        self.type_identifier("login_password_field", password)
        self.tap_identifier("login_submit_button")
        self.find_by_text("Home")

    def logout(self) -> None:
        if not self.is_logged_in():
            return
        self.open_tab("Settings")
        for _ in range(3):
            if self.has_text("LOGOUT", timeout=2):
                break
            self.swipe_up()
        self.tap_identifier("settings_logout_button")
        self.tap_text("Logout")
        self.wait_for_login()

    def open_registration(self) -> None:
        self.wait_for_login()
        self.tap_identifier("login_register_link")
        self.find_by_text("REQUEST ACCESS")

    def register(
        self,
        name: str = settings.TEST_NAME,
        email: str = settings.TEST_EMAIL,
        password: str = settings.TEST_PASSWORD,
    ) -> None:
        self.open_registration()
        self.type_identifier("register_name_field", name)
        self.type_identifier("register_email_field", email)
        self.type_identifier("register_password_field", password)
        self.tap_identifier("register_submit_button")
        self.find_by_text("Home")

    def open_tab(self, tab: str) -> None:
        if self.has_text("Synthesis Telemetry", timeout=1):
            self.driver.back()
        if not self.is_logged_in():
            self.login()
        self.tap_text(tab)
        expected = {
            "Home": "Welcome to Smart Furnace AI",
            "Dashboard": "Synthesis Dashboard",
            "History": "Synthesis History",
            "Settings": "Settings",
        }[tab]
        self.find_by_text(expected)

    def submit_empty_login(self) -> None:
        self.wait_for_login()
        self.tap_identifier("login_submit_button")

    def submit_empty_dashboard(self) -> None:
        self.open_tab("Dashboard")
        self.tap_identifier("dashboard_check_feasibility_button")
        self.find_by_text("Base and Target materials are required.")

    def run_synthesis(self, base_material: str, target_material: str) -> str:
        self.open_tab("Dashboard")
        self.type_identifier("dashboard_base_material_field", base_material)
        self.type_identifier("dashboard_target_material_field", target_material)
        self.tap_identifier("dashboard_check_feasibility_button")
        return self.wait_until_any_text(
            ["Feasibility review", "Synthesis Telemetry", "Target Temp:"],
            timeout=30,
        )

    def set_notifications(self, enabled: bool) -> None:
        self.open_tab("Settings")
        row = self.find_by_text("Notifications")
        # Switch is the first android.widget.Switch following the label.
        switch = self.driver.find_element(
            "xpath",
            '//*[@text="Notifications" or @content-desc="Notifications"]'
            '/following::android.widget.Switch[1]',
        )
        current = str(switch.get_attribute("checked")).lower() == "true"
        if current != enabled:
            switch.click()

    def measure_navigation_ms(self, tab: str) -> float:
        started = time.perf_counter()
        self.open_tab(tab)
        return (time.perf_counter() - started) * 1000

