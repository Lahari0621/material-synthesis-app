from __future__ import annotations

import time

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.support.ui import WebDriverWait

from config import settings


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(
            driver,
            settings.WAIT_SECONDS,
            ignored_exceptions=(NoSuchElementException, StaleElementReferenceException),
        )

    def find_by_identifier(self, identifier: str):
        locators = (
            (AppiumBy.ACCESSIBILITY_ID, identifier),
            (AppiumBy.ID, identifier),
            (
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().resourceId("{identifier}")',
            ),
        )
        for by, value in locators:
            try:
                return WebDriverWait(self.driver, 3).until(
                    lambda d: d.find_element(by, value)
                )
            except TimeoutException:
                continue
        text_fallbacks = {
            "login_submit_button": "ACCESS TERMINAL",
            "login_register_link": "No access? Request an account here.",
            "register_submit_button": "REGISTER SCIENTIST",
            "dashboard_check_feasibility_button": "CHECK FEASIBILITY",
            "settings_logout_button": "LOGOUT",
        }
        if identifier in text_fallbacks:
            return self.find_by_text(text_fallbacks[identifier])
        raise NoSuchElementException(f"Identifier not found: {identifier}")

    def find_by_text(self, text: str, exact: bool = True):
        escaped = text.replace('"', '\\"')
        selector = (
            f'new UiSelector().text("{escaped}")'
            if exact
            else f'new UiSelector().textContains("{escaped}")'
        )
        locators = (
            (AppiumBy.ANDROID_UIAUTOMATOR, selector),
            (AppiumBy.ACCESSIBILITY_ID, text),
            (
                AppiumBy.XPATH,
                f'//*[@text="{text}" or @content-desc="{text}"]',
            ),
        )
        for by, value in locators:
            try:
                return WebDriverWait(self.driver, 4).until(
                    lambda d: d.find_element(by, value)
                )
            except TimeoutException:
                continue
        contains_locators = (
            (
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().descriptionContains("{escaped}")',
            ),
            (
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().textContains("{escaped}")',
            ),
            (
                AppiumBy.XPATH,
                f'//*[contains(@text,"{text}") or '
                f'contains(@content-desc,"{text}")]',
            ),
        )
        for by, value in contains_locators:
            try:
                return WebDriverWait(self.driver, 3).until(
                    lambda d: d.find_element(by, value)
                )
            except TimeoutException:
                continue
        raise NoSuchElementException(f"Text not found: {text}")

    def has_text(self, text: str, timeout: int = 3, exact: bool = True) -> bool:
        original = self.wait
        try:
            self.wait = WebDriverWait(self.driver, timeout)
            self.find_by_text(text, exact=exact)
            return True
        except (NoSuchElementException, TimeoutException):
            return False
        finally:
            self.wait = original

    def tap_text(self, text: str, exact: bool = True) -> None:
        element = self.find_by_text(text, exact=exact)
        self.driver.execute_script("mobile: clickGesture", {
            "elementId": element.id,
        })

    def tap_identifier(self, identifier: str) -> None:
        element = self.find_by_identifier(identifier)
        self.driver.execute_script("mobile: clickGesture", {
            "elementId": element.id,
        })

    def type_identifier(self, identifier: str, value: str) -> None:
        element = self.find_by_identifier(identifier)
        element.click()
        element.clear()
        element.send_keys(value)
        self.driver.hide_keyboard()

    def swipe_up(self, percent: float = 0.7) -> None:
        size = self.driver.get_window_size()
        self.driver.execute_script(
            "mobile: swipeGesture",
            {
                "left": int(size["width"] * 0.1),
                "top": int(size["height"] * 0.15),
                "width": int(size["width"] * 0.8),
                "height": int(size["height"] * 0.7),
                "direction": "up",
                "percent": percent,
            },
        )

    def wait_until_any_text(self, texts: list[str], timeout: int = 20) -> str:
        deadline = time.time() + timeout
        while time.time() < deadline:
            for text in texts:
                if self.has_text(text, timeout=1, exact=False):
                    return text
        raise TimeoutException(f"None of these texts appeared: {texts}")

