const assert = require("assert");
const path = require("path");
const settings = require("../config/settings");
const { createDriver } = require("../utils/driverFactory");
const { ExcelReporter } = require("../utils/excelReporter");
const { LoginPage } = require("../pages/loginPage");
const { RegisterPage } = require("../pages/registerPage");
const { HomePage } = require("../pages/homePage");
const { DashboardPage } = require("../pages/dashboardPage");
const { HistoryPage } = require("../pages/historyPage");
const { SettingsPage } = require("../pages/settingsPage");

const reporter = new ExcelReporter(
  path.join(__dirname, "..", "reports", settings.excelReportName)
);

function record(testId, module, scenario, status, started, details = "") {
  reporter.addResult({
    testId,
    module,
    scenario,
    status,
    durationMs: (Date.now() - started),
    details,
  });
}

describe("Smart Furnace Web Selenium E2E", function () {
  this.timeout(60000);
  let driver;

  beforeEach(async function () {
    driver = await createDriver(settings.driverMode);
    if (settings.driverMode === "selenium") {
      await driver.get(settings.baseUrl);
    } else {
      await driver.get(settings.baseUrl);
    }
  });

  afterEach(async function () {
    if (driver) await driver.quit();
  });

  after(async function () {
    const out = await reporter.write();
    console.log(`\nExcel analysis report written to: ${out}`);
  });

  it("TC-01 Login screen loads with branding", async function () {
    const started = Date.now();
    try {
      await new LoginPage(driver).assertLoaded();
      record("TC-01", "Auth", "Login screen loads with branding", "PASSED", started);
    } catch (err) {
      record("TC-01", "Auth", "Login screen loads with branding", "FAILED", started, err.message);
      throw err;
    }
  });

  it("TC-02 Login rejects empty credentials", async function () {
    const started = Date.now();
    try {
      const page = new LoginPage(driver);
      await page.submit();
      assert.ok(await page.hasText("SMART FURNACE AI"));
      record("TC-02", "Auth", "Login rejects empty credentials", "PASSED", started);
    } catch (err) {
      record("TC-02", "Auth", "Login rejects empty credentials", "FAILED", started, err.message);
      throw err;
    }
  });

  it("TC-03 Navigate login -> register", async function () {
    const started = Date.now();
    try {
      await new LoginPage(driver).goToRegister();
      await new RegisterPage(driver).assertLoaded();
      record("TC-03", "Auth", "Navigate login -> register", "PASSED", started);
    } catch (err) {
      record("TC-03", "Auth", "Navigate login -> register", "FAILED", started, err.message);
      throw err;
    }
  });

  it("TC-04 Register scientist and open Home", async function () {
    const started = Date.now();
    try {
      const login = new LoginPage(driver);
      if (await login.hasText("ACCESS TERMINAL")) await login.goToRegister();
      await new RegisterPage(driver).register(
        settings.testName,
        settings.testEmail,
        settings.testPassword
      );
      await new HomePage(driver).assertLoaded();
      record("TC-04", "Auth", "Register scientist and open Home", "PASSED", started);
    } catch (err) {
      record("TC-04", "Auth", "Register scientist and open Home", "FAILED", started, err.message);
      throw err;
    }
  });

  it("TC-05 Login success reaches Home", async function () {
    const started = Date.now();
    try {
      await new LoginPage(driver).login(settings.testEmail, settings.testPassword);
      await new HomePage(driver).assertLoaded();
      record("TC-05", "Auth", "Login success reaches Home", "PASSED", started);
    } catch (err) {
      record("TC-05", "Auth", "Login success reaches Home", "FAILED", started, err.message);
      throw err;
    }
  });

  it("TC-06 Home content sections visible", async function () {
    const started = Date.now();
    try {
      await new LoginPage(driver).login(settings.testEmail, settings.testPassword);
      const home = new HomePage(driver);
      await home.assertLoaded();
      assert.ok(await home.hasText("About Our Product"));
      assert.ok(await home.hasText("Key Features"));
      record("TC-06", "Home", "Home content sections visible", "PASSED", started);
    } catch (err) {
      record("TC-06", "Home", "Home content sections visible", "FAILED", started, err.message);
      throw err;
    }
  });

  it("TC-07 Open Synthesis Dashboard", async function () {
    const started = Date.now();
    try {
      await new LoginPage(driver).login(settings.testEmail, settings.testPassword);
      await new HomePage(driver).openTab("Dashboard");
      await new DashboardPage(driver).assertLoaded();
      record("TC-07", "Dashboard", "Open Synthesis Dashboard", "PASSED", started);
    } catch (err) {
      record("TC-07", "Dashboard", "Open Synthesis Dashboard", "FAILED", started, err.message);
      throw err;
    }
  });

  it("TC-08 Validation for empty materials", async function () {
    const started = Date.now();
    try {
      await new LoginPage(driver).login(settings.testEmail, settings.testPassword);
      await new HomePage(driver).openTab("Dashboard");
      const dash = new DashboardPage(driver);
      await dash.checkFeasibility();
      assert.ok(await dash.hasText("Base and Target materials are required."));
      record("TC-08", "Dashboard", "Validation for empty materials", "PASSED", started);
    } catch (err) {
      record("TC-08", "Dashboard", "Validation for empty materials", "FAILED", started, err.message);
      throw err;
    }
  });

  it("TC-09 Run synthesis feasibility check", async function () {
    const started = Date.now();
    try {
      await new LoginPage(driver).login(settings.testEmail, settings.testPassword);
      await new HomePage(driver).openTab("Dashboard");
      const dash = new DashboardPage(driver);
      await dash.runSynthesis("Zinc", "Iron");
      const ok =
        (await dash.hasText("Feasibility review")) ||
        (await dash.hasText("Target Temp:"));
      assert.ok(ok);
      record("TC-09", "Dashboard", "Run synthesis feasibility check", "PASSED", started);
    } catch (err) {
      record("TC-09", "Dashboard", "Run synthesis feasibility check", "FAILED", started, err.message);
      throw err;
    }
  });

  it("TC-10 History screen loads", async function () {
    const started = Date.now();
    try {
      await new LoginPage(driver).login(settings.testEmail, settings.testPassword);
      await new HomePage(driver).openTab("History");
      await new HistoryPage(driver).assertLoaded();
      record("TC-10", "History", "History screen loads", "PASSED", started);
    } catch (err) {
      record("TC-10", "History", "History screen loads", "FAILED", started, err.message);
      throw err;
    }
  });

  it("TC-11 Settings screen loads", async function () {
    const started = Date.now();
    try {
      await new LoginPage(driver).login(settings.testEmail, settings.testPassword);
      await new HomePage(driver).openTab("Settings");
      await new SettingsPage(driver).assertLoaded();
      record("TC-11", "Settings", "Settings screen loads", "PASSED", started);
    } catch (err) {
      record("TC-11", "Settings", "Settings screen loads", "FAILED", started, err.message);
      throw err;
    }
  });

  it("TC-12 Logout returns to login", async function () {
    const started = Date.now();
    try {
      await new LoginPage(driver).login(settings.testEmail, settings.testPassword);
      await new HomePage(driver).openTab("Settings");
      await new SettingsPage(driver).logout();
      await new LoginPage(driver).assertLoaded();
      record("TC-12", "Settings", "Logout returns to login", "PASSED", started);
    } catch (err) {
      record("TC-12", "Settings", "Logout returns to login", "FAILED", started, err.message);
      throw err;
    }
  });

  it("TC-13 Complete register->dashboard->history->logout journey", async function () {
    const started = Date.now();
    try {
      const login = new LoginPage(driver);
      await login.goToRegister();
      await new RegisterPage(driver).register(
        settings.testName,
        settings.testEmail,
        settings.testPassword
      );
      const home = new HomePage(driver);
      await home.assertLoaded();
      await home.openTab("Dashboard");
      await new DashboardPage(driver).runSynthesis("Titanium", "Titanium");
      await home.openTab("History");
      await new HistoryPage(driver).assertLoaded();
      await home.openTab("Settings");
      await new SettingsPage(driver).logout();
      await new LoginPage(driver).assertLoaded();
      record(
        "TC-13",
        "E2E",
        "Complete register->dashboard->history->logout journey",
        "PASSED",
        started
      );
    } catch (err) {
      record(
        "TC-13",
        "E2E",
        "Complete register->dashboard->history->logout journey",
        "FAILED",
        started,
        err.message
      );
      throw err;
    }
  });
});
