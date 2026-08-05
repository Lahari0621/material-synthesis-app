from pages.base_page import BasePage


class RegisterPage(BasePage):
    def assert_loaded(self) -> None:
        assert self.has_text("REQUEST ACCESS")
        assert self.has_text("REGISTER SCIENTIST")

    def enter_name(self, name: str) -> None:
        self.type_text("name", name, fallback_label="Full Name")

    def enter_email(self, email: str) -> None:
        self.type_text("email", email, fallback_label="Institutional Email")

    def enter_password(self, password: str) -> None:
        self.type_text("password", password, fallback_label="Create Password")

    def submit(self) -> None:
        self.tap_text("REGISTER SCIENTIST")

    def register(self, name: str, email: str, password: str) -> None:
        self.enter_name(name)
        self.enter_email(email)
        self.enter_password(password)
        self.submit()
