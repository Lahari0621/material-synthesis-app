# Appium Android E2E Automation for Smart Furnace AI
#
# Folder layout (all Appium assets live here):
#   appium/
#     config/     capabilities & settings
#     pages/      page objects
#     tests/      end-to-end scenarios
#     utils/      driver factory + Excel reporter
#     reports/    generated Excel analysis
#
# Run (CI / offline deterministic Appium flow driver):
#   cd appium
#   pip install -r requirements.txt
#   python run_e2e.py --driver simulated
#
# Run against a real Android emulator/device (Appium server required):
#   appium
#   set E2E_DRIVER=appium
#   set APK_PATH=..\build\app\outputs\flutter-apk\app-debug.apk
#   python run_e2e.py --driver appium
