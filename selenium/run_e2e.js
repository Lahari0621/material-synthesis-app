#!/usr/bin/env node
const { spawnSync } = require("child_process");
const fs = require("fs");
const path = require("path");

function parseArgs(argv) {
  const out = { driver: process.env.E2E_DRIVER || "simulated" };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === "--driver" && argv[i + 1]) {
      out.driver = argv[i + 1];
      i += 1;
    }
  }
  return out;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  process.env.E2E_DRIVER = args.driver;

  console.log(`Running Selenium E2E with driver mode: ${args.driver}`);
  const mochaBin = path.join(__dirname, "node_modules", "mocha", "bin", "mocha.js");
  const result = spawnSync(
    process.execPath,
    [mochaBin, "tests/**/*.test.js", "--timeout", "60000"],
    {
      cwd: __dirname,
      stdio: "inherit",
      env: process.env,
    }
  );

  const report = path.join(
    __dirname,
    "reports",
    "Selenium_E2E_Excel_Analysis_Report.xlsx"
  );
  if (!fs.existsSync(report)) {
    console.error("WARNING: Excel report was not generated");
    process.exit(result.status === 0 ? 1 : result.status || 1);
  }
  console.log(`Excel analysis report: ${report}`);
  process.exit(result.status || 0);
}

main();
