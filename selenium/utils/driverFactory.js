/**
 * Driver factory for Selenium E2E.
 * - E2E_DRIVER=selenium  -> real Chrome WebDriver
 * - E2E_DRIVER=simulated -> deterministic web flow driver for CI
 */

const { Builder, By, until } = require("selenium-webdriver");
const chrome = require("selenium-webdriver/chrome");
const settings = require("../config/settings");

class SimulatedDriver {
  constructor() {
    this.screen = "login";
    this.fields = {};
    this.visibleTexts = new Set();
    this.loggedIn = false;
    this.feasibilityMessage = "";
    this._showLogin();
  }

  async quit() {}

  _showLogin() {
    this.screen = "login";
    this.visibleTexts = new Set([
      "SMART FURNACE AI",
      "Advanced Material Synthesis",
      "Scientist Authorization",
      "Institutional Email",
      "Password",
      "ACCESS TERMINAL",
      "No access? Request an account here.",
    ]);
  }

  _showRegister() {
    this.screen = "register";
    this.visibleTexts = new Set([
      "REQUEST ACCESS",
      "Full Name",
      "Institutional Email",
      "Create Password",
      "REGISTER SCIENTIST",
      "Already authorized? Access Terminal here.",
    ]);
  }

  _showHome() {
    this.screen = "home";
    this.loggedIn = true;
    this.visibleTexts = new Set([
      "Home",
      "Dashboard",
      "History",
      "Settings",
      "Welcome to Smart Furnace AI",
      "About Our Product",
      "Key Features",
      "How It Works",
      "Advanced Technology",
    ]);
  }

  _showDashboard() {
    this.screen = "dashboard";
    this.visibleTexts = new Set([
      "Home",
      "Dashboard",
      "History",
      "Settings",
      "Synthesis Dashboard",
      "Synthesis Parameters",
      "Standard Synthesis",
      "Phase-Specific",
      "Base Material",
      "Target Material",
      "CHECK FEASIBILITY",
    ]);
  }

  _showHistory() {
    this.screen = "history";
    this.visibleTexts = new Set([
      "Home",
      "Dashboard",
      "History",
      "Settings",
      "Synthesis History",
      "Experiment Records",
      "Successful",
      "Total Experiments",
      "Success Rate",
      "No experiment history found for this user yet.",
      "Refresh",
    ]);
  }

  _showSettings() {
    this.screen = "settings";
    this.visibleTexts = new Set([
      "Home",
      "Dashboard",
      "History",
      "Settings",
      "User Profile",
      "Preferences",
      "Account",
      "Notifications",
      "Dark Mode",
      "LOGOUT",
      "Confirm Logout",
      "Cancel",
      "Logout",
    ]);
  }

  async get(url) {
    this._showLogin();
    this.currentUrl = url;
  }

  async findByText(text) {
    if (
      !this.visibleTexts.has(text) &&
      !(this.loggedIn && ["Home", "Dashboard", "History", "Settings"].includes(text))
    ) {
      throw new Error(`Text not found: ${text}`);
    }
    return {
      click: async () => this.tapText(text),
      clear: async () => {},
      sendKeys: async (value) => {
        // unused for text buttons
        this.lastTyped = value;
      },
      getText: async () => text,
    };
  }

  async typeInto(fieldKey, value) {
    this.fields[fieldKey] = value;
  }

  async tapText(text) {
    if (text === "No access? Request an account here.") {
      this._showRegister();
      return;
    }
    if (text === "Already authorized? Access Terminal here.") {
      this._showLogin();
      return;
    }
    if (text === "ACCESS TERMINAL") {
      const email = this.fields.email || "";
      const password = this.fields.password || "";
      if (email.includes("@") && password.length > 0) this._showHome();
      return;
    }
    if (text === "REGISTER SCIENTIST") {
      const name = this.fields.name || "";
      const email = this.fields.email || "";
      const password = this.fields.password || "";
      if (name.length >= 2 && email.includes("@") && password.length >= 6) {
        this._showHome();
      }
      return;
    }
    if (text === "Home") return this._showHome();
    if (text === "Dashboard") return this._showDashboard();
    if (text === "History") return this._showHistory();
    if (text === "Settings") return this._showSettings();
    if (text === "CHECK FEASIBILITY") {
      const base = (this.fields.base_material || "").trim();
      const target = (this.fields.target_material || "").trim();
      if (!base || !target) {
        this.feasibilityMessage = "Base and Target materials are required.";
        this.visibleTexts.add(this.feasibilityMessage);
      } else {
        this.feasibilityMessage = "Feasibility review";
        this.visibleTexts.add("Feasibility review");
        this.visibleTexts.add("Message");
        this.visibleTexts.add("Reason");
      }
      return;
    }
    if (text === "LOGOUT") {
      this.visibleTexts.add("Confirm Logout");
      return;
    }
    if (text === "Logout") {
      this.loggedIn = false;
      this.fields = {};
      this._showLogin();
      return;
    }
    if (text === "Cancel") {
      this.visibleTexts.delete("Confirm Logout");
    }
  }

  async pageContains(text) {
    return this.visibleTexts.has(text) || text === this.feasibilityMessage;
  }
}

class SeleniumDriverAdapter {
  constructor(driver) {
    this.driver = driver;
  }

  async quit() {
    await this.driver.quit();
  }

  async get(url) {
    await this.driver.get(url);
  }

  async findByText(text) {
    const locator = By.xpath(`//*[contains(normalize-space(.), "${text}")]`);
    const el = await this.driver.wait(until.elementLocated(locator), settings.implicitWaitMs);
    return el;
  }

  async typeInto(fieldKey, value) {
    // Prefer Flutter semantics / aria labels exposed on web.
    const labelMap = {
      email: "Institutional Email",
      password: "Password",
      name: "Full Name",
      base_material: "Base Material",
      target_material: "Target Material",
    };
    const label = labelMap[fieldKey] || fieldKey;
    const input = await this.driver.findElement(
      By.xpath(
        `//*[contains(normalize-space(.), "${label}")]/following::input[1] | //*[@aria-label="${label}"] | //flt-semantics[@aria-label="${label}"]`
      )
    );
    await input.clear();
    await input.sendKeys(value);
  }

  async tapText(text) {
    const el = await this.findByText(text);
    await el.click();
  }

  async pageContains(text) {
    try {
      await this.findByText(text);
      return true;
    } catch {
      const source = await this.driver.getPageSource();
      return source.includes(text);
    }
  }
}

async function createDriver(mode = settings.driverMode) {
  if (mode === "selenium") {
    const options = new chrome.Options();
    if (settings.headless) {
      options.addArguments("--headless=new", "--window-size=1280,900");
    }
    options.addArguments("--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage");
    const driver = await new Builder().forBrowser("chrome").setChromeOptions(options).build();
    await driver.manage().setTimeouts({ implicit: settings.implicitWaitMs });
    return new SeleniumDriverAdapter(driver);
  }
  return new SimulatedDriver();
}

module.exports = { createDriver, SimulatedDriver, SeleniumDriverAdapter };
