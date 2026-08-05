#!/usr/bin/env bash
set -euxo pipefail

SHARD="${TEST_SHARD_INDEX:-0}"
LOG_DIR="automation/logs"
RESULT_DIR="automation/Test Results"
mkdir -p "$LOG_DIR" \
  "$RESULT_DIR/Excel" \
  "$RESULT_DIR/HTML" \
  "$RESULT_DIR/JSON" \
  "$RESULT_DIR/Screenshots" \
  "$RESULT_DIR/Logs" \
  "$RESULT_DIR/Summary"

cleanup() {
  echo "Capturing diagnostics for shard ${SHARD}" | tee -a "$LOG_DIR/emulator-diag-shard-${SHARD}.log"
  {
    echo "==== adb devices ===="
    adb devices || true
    echo "==== boot props ===="
    adb shell getprop sys.boot_completed || true
    adb shell getprop init.svc.bootanim || true
    echo "==== package list ===="
    adb shell pm list packages | grep -i smart || true
    echo "==== recent logcat ===="
    adb logcat -d -t 200 || true
  } >> "$LOG_DIR/emulator-diag-shard-${SHARD}.log" 2>&1 || true
}
trap cleanup EXIT

echo "Stage 7 · Verify emulator readiness"
adb wait-for-device
for i in $(seq 1 90); do
  BOOT="$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')"
  if [[ "$BOOT" == "1" ]]; then
    echo "Emulator boot completed"
    break
  fi
  if [[ "$i" == "90" ]]; then
    echo "Emulator never reported boot_completed=1"
    exit 1
  fi
  sleep 2
done
adb shell input keyevent 82 || true
adb devices

echo "Stage 8 · Install APK"
adb install -r "${APK_PATH}"
adb shell pm list packages | grep com.example.ai_smart_furncae_change

echo "Stage 9 · Start Appium"
nohup appium --relaxed-security \
  --log "${LOG_DIR}/appium-shard-${SHARD}.log" \
  > "${LOG_DIR}/appium-console-shard-${SHARD}.log" 2>&1 &
echo $! > "${LOG_DIR}/appium.pid"

echo "Stage 10 · Verify Appium health"
for i in $(seq 1 60); do
  if curl -sf http://127.0.0.1:4723/status >/dev/null; then
    echo "Appium is healthy"
    break
  fi
  if [[ "$i" == "60" ]]; then
    echo "Appium failed to become healthy"
    cat "${LOG_DIR}/appium-console-shard-${SHARD}.log" || true
    exit 1
  fi
  sleep 2
done

echo "Stage 11 · Execute real Appium E2E cases"
cd automation
set +e
pytest tests/test_enterprise_catalog.py --reruns 2 --reruns-delay 1 -v
TEST_EXIT=$?
set -e
echo "${TEST_EXIT}" > "logs/pytest-exit-shard-${SHARD}.txt"

echo "Stage 12-13 · Capture device screenshots and logs"
adb exec-out screencap -p > \
  "Test Results/Screenshots/final-device-shard-${SHARD}.png" || true
adb logcat -d > \
  "Test Results/Logs/device-logcat-shard-${SHARD}.txt" || true
adb shell dumpsys package com.example.ai_smart_furncae_change > \
  "Test Results/Logs/package-shard-${SHARD}.txt" || true

exit "${TEST_EXIT}"
