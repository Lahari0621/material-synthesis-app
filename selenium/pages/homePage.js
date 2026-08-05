const { BasePage } = require("./basePage");

class HomePage extends BasePage {
  async assertLoaded() {
    await this.assertHasText("Welcome to Smart Furnace AI");
    await this.assertHasText("Home");
  }

  async openTab(tabName) {
    await this.tapText(tabName);
  }
}

module.exports = { HomePage };
