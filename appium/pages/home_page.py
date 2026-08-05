from pages.base_page import BasePage


class HomePage(BasePage):
    def assert_loaded(self) -> None:
        assert self.has_text("Welcome to Smart Furnace AI")
        assert self.has_text("Home")

    def open_tab(self, tab_name: str) -> None:
        self.tap_text(tab_name)
