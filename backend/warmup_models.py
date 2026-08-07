"""Warm prediction caches before baseline load testing."""

import requests

BASE = "http://127.0.0.1:5000"
PAIRS = [
    ("Zinc", "Iron"),
    ("Iron", "Steel"),
    ("Titanium", "Titanium"),
    ("Nickel", "Nickel"),
    ("Copper", "Brass"),
    ("Aluminum", "Alumina"),
    ("Silicon", "Silica"),
    ("Carbon", "Graphite"),
]


def main() -> None:
    for base_material, target_material in PAIRS:
        requests.post(
            f"{BASE}/api/synthesis/check",
            json={
                "base_material": base_material,
                "target_material": target_material,
            },
            timeout=60,
        )
        requests.post(
            f"{BASE}/api/predict",
            json={
                "base_material": base_material,
                "target_material": target_material,
                "target_phase": "synthesis",
            },
            timeout=60,
        )
    print("Warmup complete")


if __name__ == "__main__":
    main()
