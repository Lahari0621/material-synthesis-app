const { BasePage } = require("./basePage");

class DashboardPage extends BasePage {
  async assertLoaded() {
    await this.assertHasText("Synthesis Dashboard");
    await this.assertHasText("CHECK FEASIBILITY");
  }

  async runSynthesis(baseMaterial, targetMaterial) {
    await this.type("base_material", baseMaterial);
    await this.type("target_material", targetMaterial);
    await this.tapText("CHECK FEASIBILITY");
  }

  async checkFeasibility() {
    await this.tapText("CHECK FEASIBILITY");
  }
}

module.exports = { DashboardPage };
