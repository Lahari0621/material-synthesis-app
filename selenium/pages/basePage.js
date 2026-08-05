class BasePage {
  constructor(driver) {
    this.driver = driver;
  }

  async tapText(text) {
    await this.driver.tapText(text);
  }

  async type(fieldKey, value) {
    await this.driver.typeInto(fieldKey, value);
  }

  async hasText(text) {
    return this.driver.pageContains(text);
  }

  async assertHasText(text) {
    const ok = await this.hasText(text);
    if (!ok) throw new Error(`Expected visible text: ${text}`);
  }
}

module.exports = { BasePage };
