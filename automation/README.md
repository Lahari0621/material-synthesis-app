# Enterprise Android Appium E2E

This folder contains the production Android automation framework. It uses a
real Android emulator and Appium UiAutomator2; there is no simulated driver.

## Coverage

The user-specified distribution totals **510 cases**. The generated catalog
contains all 510:

- 400 cases exercise features that exist in Smart Furnace AI.
- 110 cases are collected and reported as `BLOCKED` because Authorization,
  Search, Filters, File Upload, and portions of CRUD are not implemented in the
  application. They are not falsely reported as passed.

Regenerate and validate the catalog:

```bash
cd automation
python data/generate_test_catalog.py
pytest --collect-only -q
```

## Structure

```text
automation/
├── pages/          Page Object Model
├── tests/          Parameterized real-Appium runner
├── data/           510-case catalog and generator
├── drivers/        UiAutomator2 driver factory
├── reports/        Runtime report workspace
├── screenshots/    Runtime evidence workspace
├── logs/           Appium/backend logs
├── config/         Environment-driven configuration
├── utils/          Excel/HTML/JSON/Markdown reporting
├── listeners/      Listener extension point
├── runners/        Local execution scripts
├── resources/      Deterministic E2E API
└── Test Results/
    ├── Excel/
    ├── HTML/
    ├── JSON/
    ├── Screenshots/
    ├── Logs/
    └── Summary/
```

## Local execution

Prerequisites:

- Flutter stable and Android SDK
- Java 17
- Node.js 20+
- Android emulator/device visible in `adb devices`
- Appium and UiAutomator2
- Python 3.11+

```bash
flutter pub get
flutter build apk --debug

npm install --global appium
appium driver install uiautomator2
appium --relaxed-security

python automation/resources/mock_backend.py

cd automation
python -m pip install -r requirements.txt
python data/generate_test_catalog.py
pytest tests/test_enterprise_catalog.py --reruns 2 --reruns-delay 1 -v
python utils/report_generator.py --input "Test Results" --output "Test Results"
```

Override configuration with environment variables:

- `APPIUM_SERVER_URL`
- `ANDROID_UDID`
- `ANDROID_VERSION`
- `APK_PATH`
- `TEST_SHARD_INDEX` / `TEST_SHARD_TOTAL`
- `CRITICAL_FAILURE_THRESHOLD`
- `PERFORMANCE_LIMIT_MS`

## CI/CD

`.github/workflows/android-e2e.yml` runs on push, pull request, manual
dispatch, and nightly schedule:

1. Build and upload the debug APK.
2. Run four parallel Android emulator shards.
3. Start Appium and UiAutomator2.
4. Install the APK and execute all 510 collected cases.
5. Retry failures twice.
6. Capture screenshots, logcat, package diagnostics, backend logs, and Appium
   logs.
7. Aggregate Excel, HTML, JSON, and Markdown reports.
8. Enforce at least 95% pass rate and at most 5% critical failure rate.
9. Upload all evidence for 30 days.

`.github/workflows/deploy-reports.yml` downloads the completed report,
publishes `reports/latest/`, and archives it under
`reports/history/build-N/` on the `gh-pages` branch.

Expected live URL:

`https://chaithanyaneelam.github.io/material-synthesis-app/reports/latest/execution-report.html`

## Repository configuration

The workflows use only `GITHUB_TOKEN`; no application secrets are required.
Repository Actions permissions must allow read/write workflows:

1. Settings → Actions → General → Workflow permissions.
2. Select **Read and write permissions**.
3. In Settings → Pages, choose the `gh-pages` branch after its first
   deployment if GitHub does not select it automatically.

Branch protection should require:

- `Stage 1-5 · Build Android APK`
- all four `Appium shard N of 4` jobs
- `Stage 14-18 · Reports, summary, artifacts`

## Troubleshooting

- **Emulator boot failure:** inspect the emulator-runner job and increase its
  timeout; confirm API level 35 is available.
- **APK install failure:** download `android-debug-apk`, run
  `aapt dump badging`, and inspect `adb install` output.
- **Appium unhealthy:** inspect `appium-console-shard-N.log`; run
  `appium driver list --installed`.
- **Selectors missing:** inspect `adb shell uiautomator dump` and preserve
  Flutter `Semantics(identifier: ...)` wrappers.
- **Mock API unavailable:** inspect `mock-backend-shard-N.log`; Android
  emulators access the runner host at `10.0.2.2:5000`.
- **Report aggregation failure:** one or more shards did not produce its
  unique `shard-N-results.json`; treat this as infrastructure failure.
- **Pages not visible:** confirm `gh-pages` exists and is selected in
  Settings → Pages.

