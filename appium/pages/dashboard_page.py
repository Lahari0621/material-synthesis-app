from pages.base_page import BasePage


class DashboardPage(BasePage):
    def assert_loaded(self) -> None:
        assert self.has_text("Synthesis Dashboard")
        assert self.has_text("CHECK FEASIBILITY")

    def enter_base_material(self, value: str) -> None:
        self.type_text("base_material", value, fallback_label="Base Material")

    def enter_target_material(self, value: str) -> None:
        self.type_text("target_material", value, fallback_label="Target Material")

    def check_feasibility(self) -> None:
        self.tap_text("CHECK FEASIBILITY")

    def run_synthesis(self, base_material: str, target_material: str) -> None:
        self.enter_base_material(base_material)
        self.enter_target_material(target_material)
        self.check_feasibility()
