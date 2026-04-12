"""Gateway client — live interaction with an Ignition gateway via WebDev REST endpoints.

Expects the Ignition gateway to have a WebDev module with endpoints:
  POST /system/webdev/api/tags/read     — read tag values
  POST /system/webdev/api/tags/write    — write tag values
  POST /system/webdev/api/script/run    — execute a script
  POST /system/webdev/api/history/query — query tag history
"""

from __future__ import annotations

from typing import Any

import httpx


class GatewayClient:
    """HTTP client for Ignition WebDev API endpoints."""

    def __init__(self, base_url: str, username: str = "", password: str = "", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self._auth = (username, password) if username else None
        self._timeout = timeout

    def _post(self, path: str, payload: dict[str, Any]) -> Any:
        url = f"{self.base_url}{path}"
        resp = httpx.post(url, json=payload, auth=self._auth, timeout=self._timeout)
        resp.raise_for_status()
        return resp.json()

    def read_tags(self, tag_paths: list[str]) -> list[dict[str, Any]]:
        """Read current values of one or more tags."""
        result = self._post("/system/webdev/api/tags/read", {"tagPaths": tag_paths})
        return result if isinstance(result, list) else [result]

    def write_tag(self, tag_path: str, value: Any) -> dict[str, Any]:
        """Write a value to a tag. Returns write result with quality."""
        return self._post("/system/webdev/api/tags/write", {"tagPath": tag_path, "value": value})

    def execute_script(self, code: str) -> dict[str, Any]:
        """Execute a Python script on the gateway and return the result."""
        return self._post("/system/webdev/api/script/run", {"code": code})

    def query_history(self, tag_path: str, start: str, end: str) -> dict[str, Any]:
        """Query tag history. start/end are ISO 8601 timestamps."""
        return self._post(
            "/system/webdev/api/history/query",
            {"tagPath": tag_path, "startDate": start, "endDate": end},
        )
