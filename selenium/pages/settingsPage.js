const { BasePage } = require("./basePage");

class SettingsPage extends BasePage {
  async assertLoaded() {
    const hasSettings = await this.hasText("Settings");
    const hasProfile = await this.hasText("User Profile");
    if (!hasSettings && !hasProfile) {
      throw new Error("Settings screen not loaded");
    }
    await this.assertHasText("LOGOUT");
  }

  async logout() {
    await this.tapText("LOGOUT");
    await this.tapText("Logout");
  }
}

module.exports = { SettingsPage };
