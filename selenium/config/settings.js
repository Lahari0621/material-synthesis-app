module.exports = {
  baseUrl: process.env.BASE_URL || "http://127.0.0.1:8080",
  // selenium = real Chrome WebDriver, simulated = CI-safe flow driver
  driverMode: (process.env.E2E_DRIVER || "simulated").toLowerCase(),
  headless: (process.env.HEADLESS || "true").toLowerCase() !== "false",
  implicitWaitMs: Number(process.env.IMPLICIT_WAIT_MS || 8000),
  testEmail: process.env.E2E_EMAIL || "scientist@smartfurnace.test",
  testPassword: process.env.E2E_PASSWORD || "Passw0rd!",
  testName: process.env.E2E_NAME || "Baseline Scientist",
  excelReportName:
    process.env.EXCEL_REPORT_NAME || "Selenium_E2E_Excel_Analysis_Report.xlsx",
};
