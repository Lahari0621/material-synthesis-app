const ExcelJS = require("exceljs");
const path = require("path");
const fs = require("fs");

class ExcelReporter {
  constructor(outputPath) {
    this.outputPath = outputPath;
    this.rows = [];
  }

  addResult({ testId, module, scenario, status, durationMs, details = "" }) {
    this.rows.push({
      testId,
      module,
      scenario,
      status: String(status).toUpperCase(),
      durationMs: Number(durationMs.toFixed(1)),
      details,
      executedAt: new Date().toISOString(),
    });
  }

  async write() {
    const workbook = new ExcelJS.Workbook();
    const summary = workbook.addWorksheet("Summary");
    const details = workbook.addWorksheet("Test Cases");
    const analysis = workbook.addWorksheet("Excel Analysis");

    const passed = this.rows.filter((r) => r.status === "PASSED").length;
    const failed = this.rows.filter((r) => r.status === "FAILED").length;
    const total = this.rows.length;
    const passRate = total ? Number(((passed / total) * 100).toFixed(2)) : 0;

    summary.addRow(["Metric", "Value"]);
    summary.addRow(["Total Test Cases", total]);
    summary.addRow(["Passed", passed]);
    summary.addRow(["Failed", failed]);
    summary.addRow(["Pass Rate (%)", passRate]);
    summary.addRow(["Generated At", new Date().toISOString()]);
    summary.addRow(["Framework", "Selenium Web E2E + Excel Analysis (Node.js)"]);
    this.#styleHeader(summary);

    details.addRow([
      "Test ID",
      "Module",
      "Scenario",
      "Status",
      "Duration (ms)",
      "Details",
      "Executed At",
    ]);
    for (const row of this.rows) {
      details.addRow([
        row.testId,
        row.module,
        row.scenario,
        row.status,
        row.durationMs,
        row.details,
        row.executedAt,
      ]);
    }
    this.#styleHeader(details);
    this.#colorStatus(details);

    analysis.addRow(["Module", "Total", "Passed", "Failed", "Pass Rate (%)"]);
    const modules = {};
    for (const row of this.rows) {
      if (!modules[row.module]) {
        modules[row.module] = { total: 0, passed: 0, failed: 0 };
      }
      modules[row.module].total += 1;
      if (row.status === "PASSED") modules[row.module].passed += 1;
      else modules[row.module].failed += 1;
    }
    for (const [module, stats] of Object.entries(modules).sort()) {
      const rate = stats.total
        ? Number(((stats.passed / stats.total) * 100).toFixed(2))
        : 0;
      analysis.addRow([module, stats.total, stats.passed, stats.failed, rate]);
    }
    this.#styleHeader(analysis);

    fs.mkdirSync(path.dirname(this.outputPath), { recursive: true });
    await workbook.xlsx.writeFile(this.outputPath);
    return this.outputPath;
  }

  #styleHeader(sheet) {
    const row = sheet.getRow(1);
    row.font = { bold: true, color: { argb: "FFFFFFFF" } };
    row.fill = {
      type: "pattern",
      pattern: "solid",
      fgColor: { argb: "FF1F4E79" },
    };
  }

  #colorStatus(sheet) {
    sheet.eachRow((row, rowNumber) => {
      if (rowNumber === 1) return;
      const cell = row.getCell(4);
      const value = String(cell.value || "").toUpperCase();
      if (value === "PASSED") {
        cell.fill = {
          type: "pattern",
          pattern: "solid",
          fgColor: { argb: "FFC6EFCE" },
        };
      } else if (value === "FAILED") {
        cell.fill = {
          type: "pattern",
          pattern: "solid",
          fgColor: { argb: "FFFFC7CE" },
        };
      }
    });
  }
}

module.exports = { ExcelReporter };
