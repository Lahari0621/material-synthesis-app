"""Generate the authoritative 510-case executable Appium catalog."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "test_cases.json"

# The requested distribution sums to 510 (not 400).
DISTRIBUTION = {
    "Authentication": 40,
    "Authorization": 30,
    "Registration": 20,
    "Profile Management": 20,
    "Navigation": 30,
    "Dashboard": 20,
    "Forms": 40,
    "CRUD Operations": 40,
    "Search": 20,
    "Filters": 20,
    "Input Validation": 40,
    "Error Handling": 20,
    "Session Management": 20,
    "Notifications": 20,
    "File Upload": 20,
    "Offline Handling": 10,
    "Accessibility": 20,
    "Responsive UI": 10,
    "Performance Smoke Tests": 20,
    "Regression Suite": 50,
}

PREFIXES = {
    "Authentication": "AUTH",
    "Authorization": "AUTHZ",
    "Registration": "REG",
    "Profile Management": "PROFILE",
    "Navigation": "NAV",
    "Dashboard": "DASH",
    "Forms": "FORM",
    "CRUD Operations": "CRUD",
    "Search": "SEARCH",
    "Filters": "FILTER",
    "Input Validation": "VALID",
    "Error Handling": "ERROR",
    "Session Management": "SESSION",
    "Notifications": "NOTIFY",
    "File Upload": "FILE",
    "Offline Handling": "OFFLINE",
    "Accessibility": "A11Y",
    "Responsive UI": "RESP",
    "Performance Smoke Tests": "PERF",
    "Regression Suite": "REGR",
}

HANDLERS = {
    "Authentication": ["login_screen", "invalid_login", "valid_login", "logout"],
    "Authorization": ["blocked_authorization"],
    "Registration": ["registration_screen", "registration_validation"],
    "Profile Management": ["profile_read_only"],
    "Navigation": ["navigation"],
    "Dashboard": ["dashboard", "dashboard_validation", "synthesis"],
    "Forms": ["form_presence", "form_entry"],
    "CRUD Operations": ["history_read", "blocked_crud"],
    "Search": ["blocked_search"],
    "Filters": ["blocked_filters"],
    "Input Validation": ["input_validation"],
    "Error Handling": ["error_handling"],
    "Session Management": ["session"],
    "Notifications": ["notifications"],
    "File Upload": ["blocked_file_upload"],
    "Offline Handling": ["offline"],
    "Accessibility": ["accessibility"],
    "Responsive UI": ["responsive"],
    "Performance Smoke Tests": ["performance"],
    "Regression Suite": [
        "login_screen",
        "navigation",
        "dashboard",
        "history_read",
        "profile_read_only",
        "logout",
    ],
}

BLOCKED_HANDLERS = {
    "blocked_authorization":
        "Role/permission controls are not implemented in the application.",
    "blocked_crud":
        "Create/update/delete history controls are not implemented.",
    "blocked_search": "Search is not implemented in the application.",
    "blocked_filters": "Filtering is not implemented in the application.",
    "blocked_file_upload": "File upload is not implemented in the application.",
}


def build_case(module: str, index: int) -> dict:
    handler = HANDLERS[module][(index - 1) % len(HANDLERS[module])]
    blocked_reason = BLOCKED_HANDLERS.get(handler)
    priority = "Critical" if index <= max(2, DISTRIBUTION[module] // 5) else (
        "High" if index % 3 else "Medium"
    )
    test_id = f"TC_{PREFIXES[module]}_{index:03d}"
    variant = ((index - 1) % 10) + 1
    return {
        "test_id": test_id,
        "module": module,
        "test_name": f"{module} scenario {index:03d}",
        "priority": priority,
        "preconditions": "APK installed; emulator and Appium server healthy",
        "test_steps": [
            f"Launch Smart Furnace Android application for {module}",
            f"Execute data-driven variant {variant}",
            "Verify the expected UI state and application response",
        ],
        "test_data": {
            "variant": variant,
            "email": f"scientist+{index}@smartfurnace.test",
            "base_material": ["Zinc", "Iron", "Titanium", "Nickel"][index % 4],
            "target_material": ["Iron", "Steel", "Titanium", "Nickel"][index % 4],
        },
        "expected_result": (
            blocked_reason
            if blocked_reason
            else f"{module} variant {variant} completes with the expected UI state"
        ),
        "actual_result": "",
        "status": "NOT_RUN",
        "handler": handler,
        "blocked_reason": blocked_reason,
    }


def main() -> None:
    cases = [
        build_case(module, index)
        for module, count in DISTRIBUTION.items()
        for index in range(1, count + 1)
    ]
    assert len(cases) == 510
    assert len({case["test_id"] for case in cases}) == 510
    OUTPUT.write_text(json.dumps(cases, indent=2), encoding="utf-8")
    print(f"Generated {len(cases)} executable cases at {OUTPUT}")


if __name__ == "__main__":
    main()

