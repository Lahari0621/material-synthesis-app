"""Deterministic API double used by Android UI E2E tests."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


USER = {
    "id": 1,
    "username": "Automation Scientist",
    "email": "scientist@smartfurnace.test",
}
HISTORY = [
    {
        "id": 1,
        "base_material": "Titanium",
        "target_material": "Titanium",
        "optimal_temp_c": 1450.0,
        "heating_duration_min": 45,
        "confidence_score": 98.0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
]


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[mock-api] {format % args}", flush=True)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if not length:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _send(self, status: int, payload: dict):
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            return self._send(200, {"status": "ok"})
        if path.startswith("/api/history/"):
            return self._send(200, {"history": HISTORY})
        return self._send(404, {"error": "Not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        body = self._body()

        if path == "/api/login":
            if (
                body.get("email") == USER["email"]
                and body.get("password") == "Passw0rd!"
            ):
                return self._send(200, {"message": "Login successful", "user": USER})
            return self._send(401, {"error": "Invalid email or password"})

        if path == "/api/register":
            user = {
                "id": 1,
                "username": body.get("username", USER["username"]),
                "email": body.get("email", USER["email"]),
            }
            return self._send(
                201, {"message": "User registered successfully!", "user": user}
            )

        if path == "/api/logout":
            return self._send(200, {"message": "Logout successful", "user_id": 1})

        if path in ("/api/predict", "/api/synthesis/check"):
            base = str(body.get("base_material", ""))
            target = str(body.get("target_material", ""))
            if not base or not target:
                return self._send(
                    400, {"error": "base_material and target_material are required"}
                )
            if base.lower() == target.lower():
                payload = {
                    "feasible": True,
                    "optimal_temperature_c": 1450.0,
                    "achievable_product": target,
                    "confidence_score": 98.0,
                    "notes": "Deterministic E2E response",
                }
                return self._send(200, payload)
            payload = {
                "feasible": False,
                "message": f"Direct transformation from {base} to {target} is not feasible.",
                "reason": "E2E deterministic feasibility result.",
                "recommendations": ["Use a compatible target material."],
            }
            return self._send(400, payload)

        return self._send(404, {"error": "Not found"})


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 5000), Handler)
    print("Mock backend listening on http://0.0.0.0:5000", flush=True)
    server.serve_forever()

