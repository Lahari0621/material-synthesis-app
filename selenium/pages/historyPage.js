const { BasePage } = require("./basePage");

class HistoryPage extends BasePage {
  async assertLoaded() {
    await this.assertHasText("Synthesis History");
    await this.assertHasText("Experiment Records");
  }
}

module.exports = { HistoryPage };
