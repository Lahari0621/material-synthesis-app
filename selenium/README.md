# Selenium Web E2E Automation (Node.js) for Smart Furnace AI

All Selenium assets live in this folder:

```
selenium/
  config/     settings
  pages/      page objects
  tests/      end-to-end scenarios
  utils/      driver factory + Excel reporter
  reports/    generated Excel analysis
```

## Run (CI / offline deterministic flow driver)

```bash
cd selenium
npm install
npm run test:simulated
```

## Run against a live Flutter web app (Chrome)

```bash
# terminal 1
cd ..
flutter run -d chrome --web-port 8080

# terminal 2
cd selenium
set E2E_DRIVER=selenium
set BASE_URL=http://127.0.0.1:8080
npm run test:selenium
```

Excel report output:
`reports/Selenium_E2E_Excel_Analysis_Report.xlsx`
