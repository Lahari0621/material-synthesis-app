from __future__ import annotations

import json
from collections import Counter

from data.generate_test_catalog import DISTRIBUTION
from utils.report_generator import generate


def test_catalog_has_requested_510_case_distribution():
    cases = json.load(open("data/test_cases.json", encoding="utf-8"))
    assert len(cases) == 510
    assert len({case["test_id"] for case in cases}) == 510
    assert Counter(case["module"] for case in cases) == DISTRIBUTION
    assert all(case["test_steps"] for case in cases)
    assert all(case["expected_result"] for case in cases)


def test_all_report_formats_are_generated(tmp_path):
    cases = json.load(open("data/test_cases.json", encoding="utf-8"))
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()

    for index in range(4):
        rows = []
        for offset, case in enumerate(cases):
            if offset % 4 != index:
                continue
            row = dict(case)
            row["status"] = "BLOCKED" if case["blocked_reason"] else "PASSED"
            row["actual_result"] = (
                case["blocked_reason"] or "Synthetic report contract validation"
            )
            row["execution_time_ms"] = 1.0
            rows.append(row)
        payload = {
            "metadata": {
                "device": "Contract Test",
                "android_version": "35",
                "shard_index": index,
            },
            "results": rows,
        }
        (input_root / f"shard-{index}-results.json").write_text(
            json.dumps(payload), encoding="utf-8"
        )

    metrics, code = generate(input_root, output_root)
    assert code == 0
    assert metrics["total"] == 510
    assert metrics["blocked"] == 110
    assert metrics["passed"] == 400
    expected = [
        "Excel/Automation_Test_Report.xlsx",
        "Excel/Passed_Test_Cases.xlsx",
        "Excel/Failed_Test_Cases.xlsx",
        "Excel/Execution_Summary.xlsx",
        "HTML/execution-report.html",
        "HTML/dashboard.html",
        "HTML/trends.html",
        "JSON/execution-results.json",
        "Summary/summary.md",
    ]
    assert all((output_root / relative).is_file() for relative in expected)

