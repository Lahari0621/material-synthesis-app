const { BasePage } = require("./basePage");

class RegisterPage extends BasePage {
  async assertLoaded() {
    await this.assertHasText("REQUEST ACCESS");
    await this.assertHasText("REGISTER SCIENTIST");
  }

  async register(name, email, password) {
    await this.type("name", name);
    await this.type("email", email);
    await this.type("password", password);
    await this.tapText("REGISTER SCIENTIST");
  }
}

module.exports = { RegisterPage };
