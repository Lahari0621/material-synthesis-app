from __future__ import annotations

from config import settings
from utils.driver_factory import SimulatedDriver


class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def is_simulated(self) -> bool:
        return isinstance(self.driver, SimulatedDriver)

    def tap_text(self, text: str) -> None:
        if self.is_simulated():
            self.driver.tap_text(text)
            return
        el = self.driver.find_element("xpath", f'//*[@text="{text}"]')
        el.click()

    def type_text(self, field_key: str, value: str, fallback_label: str | None = None) -> None:
        if self.is_simulated():
            self.driver.type_into(field_key, value)
            return
        # Real Appium: prefer content-desc/resource-id style keys when present,
        # otherwise fall back to labeled EditText near label text.
        try:
            el = self.driver.find_element("accessibility id", field_key)
        except Exception:
            if fallback_label:
                el = self.driver.find_element(
                    "xpath",
                    f'//*[contains(@text,"{fallback_label}")]/following::android.widget.EditText[1]',
                )
            else:
                raise
        el.clear()
        el.send_keys(value)

    def has_text(self, text: str) -> bool:
        if self.is_simulated():
            return self.driver.page_source_contains(text)
        try:
            self.driver.find_element("xpath", f'//*[@text="{text}"]')
            return True
        except Exception:
            return False

    def wait_for_text(self, text: str) -> None:
        if self.has_text(text):
            return
        if self.is_simulated():
            raise AssertionError(f"Text not visible in simulated UI: {text}")
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By

        WebDriverWait(self.driver, settings.EXPLICIT_WAIT_SEC).until(
            EC.presence_of_element_located((By.XPATH, f'//*[@text="{text}"]'))
        )
