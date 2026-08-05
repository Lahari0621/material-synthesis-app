from pages.base_page import BasePage


class HistoryPage(BasePage):
    def assert_loaded(self) -> None:
        assert self.has_text("Synthesis History")
        assert self.has_text("Experiment Records")
