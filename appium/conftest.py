from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import settings
from utils.driver_factory import create_driver
from utils.excel_reporter import ExcelReporter


@pytest.fixture(scope="session")
def excel_reporter():
    report_path = settings.REPORTS_DIR / settings.EXCEL_REPORT_NAME
    reporter = ExcelReporter(report_path)
    yield reporter
    out = reporter.write()
    print(f"\nExcel analysis report written to: {out}")


@pytest.fixture
def driver():
    drv = create_driver()
    yield drv
    try:
        drv.quit()
    except Exception:
        pass


@pytest.fixture
def record(excel_reporter):
    def _record(test_id, module, scenario, status, started, details=""):
        excel_reporter.add_result(
            test_id=test_id,
            module=module,
            scenario=scenario,
            status=status,
            duration_ms=(time.perf_counter() - started) * 1000.0,
            details=details,
        )

    return _record
