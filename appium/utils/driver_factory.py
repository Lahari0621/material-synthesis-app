"""
Driver factory for Appium E2E.

- E2E_DRIVER=appium  -> real Appium UiAutomator2 session
- E2E_DRIVER=simulated -> deterministic flow driver for CI / offline runs
"""

from __future__ import annotations

from dataclasses import dataclass, field

from config import settings


class ElementNotFound(Exception):
    pass


@dataclass
class SimElement:
    text: str = ""
    content_desc: str = ""
    enabled: bool = True

    def click(self) -> None:
        return None

    def clear(self) -> None:
        return None

    def send_keys(self, value: str) -> None:
        self.text = value


@dataclass
class SimulatedDriver:
    """In-memory UI state machine mirroring Smart Furnace Android screens."""

    screen: str = "login"
    fields: dict[str, str] = field(default_factory=dict)
    visible_texts: set[str] = field(default_factory=set)
    logged_in: bool = False
    feasibility_message: str = ""

    def __post_init__(self) -> None:
        self._show_login()

    def quit(self) -> None:
        return None

    def implicit_wait(self, _seconds: int) -> None:
        return None

    def _show_login(self) -> None:
        self.screen = "login"
        self.visible_texts = {
            "SMART FURNACE AI",
            "Advanced Material Synthesis",
            "Scientist Authorization",
            "Institutional Email",
            "Password",
            "ACCESS TERMINAL",
            "No access? Request an account here.",
        }

    def _show_register(self) -> None:
        self.screen = "register"
        self.visible_texts = {
            "REQUEST ACCESS",
            "Full Name",
            "Institutional Email",
            "Create Password",
            "REGISTER SCIENTIST",
            "Already authorized? Access Terminal here.",
        }

    def _show_home(self) -> None:
        self.screen = "home"
        self.logged_in = True
        self.visible_texts = {
            "Home",
            "Dashboard",
            "History",
            "Settings",
            "Welcome to Smart Furnace AI",
            "About Our Product",
            "Key Features",
            "How It Works",
            "Advanced Technology",
        }

    def _show_dashboard(self) -> None:
        self.screen = "dashboard"
        self.visible_texts = {
            "Home",
            "Dashboard",
            "History",
            "Settings",
            "Synthesis Dashboard",
            "Synthesis Parameters",
            "Standard Synthesis",
            "Phase-Specific",
            "Base Material",
            "Target Material",
            "CHECK FEASIBILITY",
        }

    def _show_history(self) -> None:
        self.screen = "history"
        self.visible_texts = {
            "Home",
            "Dashboard",
            "History",
            "Settings",
            "Synthesis History",
            "Experiment Records",
            "Successful",
            "Total Experiments",
            "Success Rate",
            "No experiment history found for this user yet.",
            "Refresh",
        }

    def _show_settings(self) -> None:
        self.screen = "settings"
        self.visible_texts = {
            "Home",
            "Dashboard",
            "History",
            "Settings",
            "User Profile",
            "Preferences",
            "Account",
            "Notifications",
            "Dark Mode",
            "LOGOUT",
            "Confirm Logout",
            "Cancel",
            "Logout",
        }

    def find_element(self, by: str, value: str) -> SimElement:
        key = value
        mapping = {
            "login_email_field": "email",
            "login_password_field": "password",
            "login_submit_button": "ACCESS TERMINAL",
            "login_register_link": "No access? Request an account here.",
            "register_name_field": "name",
            "register_email_field": "email",
            "register_password_field": "password",
            "register_submit_button": "REGISTER SCIENTIST",
            "dashboard_base_material_field": "base_material",
            "dashboard_target_material_field": "target_material",
            "dashboard_check_feasibility_button": "CHECK FEASIBILITY",
            "settings_logout_button": "LOGOUT",
        }

        if by in {"id", "accessibility id", "-android uiautomator"}:
            if key in mapping and mapping[key] in {
                "email",
                "password",
                "name",
                "base_material",
                "target_material",
            }:
                return SimElement(text=self.fields.get(mapping[key], ""))
            if key in mapping:
                return SimElement(text=mapping[key])

        if by == "xpath" and "ACCESS TERMINAL" in value:
            return SimElement(text="ACCESS TERMINAL")
        if by == "xpath" and "REGISTER SCIENTIST" in value:
            return SimElement(text="REGISTER SCIENTIST")
        if by == "xpath" and "CHECK FEASIBILITY" in value:
            return SimElement(text="CHECK FEASIBILITY")
        if by == "xpath" and "LOGOUT" in value:
            return SimElement(text="LOGOUT")
        if by == "xpath" and "Logout" in value:
            return SimElement(text="Logout")

        raise ElementNotFound(f"{by}={value}")

    def find_elements(self, by: str, value: str) -> list[SimElement]:
        try:
            return [self.find_element(by, value)]
        except ElementNotFound:
            return []

    def find_by_text(self, text: str) -> SimElement:
        if text not in self.visible_texts and text not in {
            "ACCESS TERMINAL",
            "REGISTER SCIENTIST",
            "CHECK FEASIBILITY",
            "LOGOUT",
            "Logout",
            "Cancel",
            "Home",
            "Dashboard",
            "History",
            "Settings",
        }:
            # Allow navigation labels always while logged in
            if self.logged_in and text in {"Home", "Dashboard", "History", "Settings"}:
                return SimElement(text=text)
            raise ElementNotFound(text)
        return SimElement(text=text)

    def tap_text(self, text: str) -> None:
        if text == "No access? Request an account here.":
            self._show_register()
            return
        if text == "Already authorized? Access Terminal here.":
            self._show_login()
            return
        if text == "ACCESS TERMINAL":
            email = self.fields.get("email", "")
            password = self.fields.get("password", "")
            if "@" in email and len(password) > 0:
                self._show_home()
            return
        if text == "REGISTER SCIENTIST":
            name = self.fields.get("name", "")
            email = self.fields.get("email", "")
            password = self.fields.get("password", "")
            if len(name) >= 2 and "@" in email and len(password) >= 6:
                self._show_home()
            return
        if text == "Home":
            self._show_home()
            return
        if text == "Dashboard":
            self._show_dashboard()
            return
        if text == "History":
            self._show_history()
            return
        if text == "Settings":
            self._show_settings()
            return
        if text == "CHECK FEASIBILITY":
            base = self.fields.get("base_material", "").strip()
            target = self.fields.get("target_material", "").strip()
            if not base or not target:
                self.feasibility_message = "Base and Target materials are required."
                self.visible_texts.add(self.feasibility_message)
            else:
                self.feasibility_message = "Feasibility review"
                self.visible_texts.add("Feasibility review")
                self.visible_texts.add("Message")
                self.visible_texts.add("Reason")
            return
        if text == "LOGOUT":
            self.visible_texts.add("Confirm Logout")
            return
        if text == "Logout":
            self.logged_in = False
            self.fields.clear()
            self._show_login()
            return
        if text == "Cancel":
            self.visible_texts.discard("Confirm Logout")
            return

    def type_into(self, field_key: str, value: str) -> None:
        self.fields[field_key] = value

    def page_source_contains(self, text: str) -> bool:
        return text in self.visible_texts or text == self.feasibility_message


def create_driver():
    if settings.E2E_DRIVER == "appium":
        from appium import webdriver
        from appium.options.android import UiAutomator2Options

        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.device_name = "Android Emulator"
        options.app = settings.APK_PATH
        options.app_package = settings.APP_PACKAGE
        options.app_activity = settings.APP_ACTIVITY
        options.automation_name = "UiAutomator2"
        options.no_reset = False
        options.new_command_timeout = 120
        driver = webdriver.Remote(settings.APPIUM_SERVER_URL, options=options)
        driver.implicitly_wait(settings.IMPLICIT_WAIT_SEC)
        return driver

    return SimulatedDriver()
