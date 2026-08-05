const { BasePage } = require("./basePage");

class LoginPage extends BasePage {
  async assertLoaded() {
    await this.assertHasText("SMART FURNACE AI");
    await this.assertHasText("ACCESS TERMINAL");
  }

  async enterEmail(email) {
    await this.type("email", email);
  }

  async enterPassword(password) {
    await this.type("password", password);
  }

  async submit() {
    await this.tapText("ACCESS TERMINAL");
  }

  async goToRegister() {
    await this.tapText("No access? Request an account here.");
  }

  async login(email, password) {
    await this.enterEmail(email);
    await this.enterPassword(password);
    await this.submit();
  }
}

module.exports = { LoginPage };
