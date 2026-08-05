from pages.base_page import BasePage


class LoginPage(BasePage):
    def assert_loaded(self) -> None:
        assert self.has_text("SMART FURNACE AI")
        assert self.has_text("ACCESS TERMINAL")

    def enter_email(self, email: str) -> None:
        self.type_text("email", email, fallback_label="Institutional Email")

    def enter_password(self, password: str) -> None:
        self.type_text("password", password, fallback_label="Password")

    def submit(self) -> None:
        self.tap_text("ACCESS TERMINAL")

    def go_to_register(self) -> None:
        self.tap_text("No access? Request an account here.")

    def login(self, email: str, password: str) -> None:
        self.enter_email(email)
        self.enter_password(password)
        self.submit()
