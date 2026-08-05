from pages.base_page import BasePage


class SettingsPage(BasePage):
    def assert_loaded(self) -> None:
        assert self.has_text("Settings") or self.has_text("User Profile")
        assert self.has_text("LOGOUT")

    def logout(self) -> None:
        self.tap_text("LOGOUT")
        # Confirm dialog
        self.tap_text("Logout")
