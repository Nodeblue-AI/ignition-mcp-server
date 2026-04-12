"""Tests for live gateway tools using a mock HTTP server."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from ignition_mcp_server.gateway_client import GatewayClient


class MockGatewayHandler(BaseHTTPRequestHandler):
    """Mock Ignition WebDev API endpoints."""

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        if self.path == "/system/webdev/api/tags/read":
            resp = [
                {"path": p, "value": 1750.5 if "Speed" in p else True, "quality": "Good"}
                for p in body.get("tagPaths", [])
            ]
        elif self.path == "/system/webdev/api/tags/write":
            resp = {"path": body["tagPath"], "quality": "Good", "written": True}
        elif self.path == "/system/webdev/api/script/run":
            resp = {"result": "script executed", "code": body.get("code", "")}
        elif self.path == "/system/webdev/api/history/query":
            resp = {
                "tagPath": body["tagPath"],
                "startDate": body["startDate"],
                "endDate": body["endDate"],
                "data": [
                    {"timestamp": "2026-04-12T00:00:00Z", "value": 1700.0},
                    {"timestamp": "2026-04-12T06:00:00Z", "value": 1750.5},
                ],
            }
        else:
            self.send_response(404)
            self.end_headers()
            return

        payload = json.dumps(resp).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        pass  # suppress request logging


@pytest.fixture(scope="module")
def mock_gateway():
    """Start a mock gateway HTTP server for the test module."""
    server = HTTPServer(("127.0.0.1", 0), MockGatewayHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()


@pytest.fixture
def client(mock_gateway):
    return GatewayClient(mock_gateway)


# ── GatewayClient direct tests ─────────────────────────────


class TestGatewayClient:
    def test_read_single_tag(self, client):
        result = client.read_tags(["[default]Conveyors/Line1/Speed"])
        assert len(result) == 1
        assert result[0]["value"] == 1750.5
        assert result[0]["quality"] == "Good"

    def test_read_multiple_tags(self, client):
        result = client.read_tags([
            "[default]Conveyors/Line1/Speed",
            "[default]Conveyors/Line1/Running",
        ])
        assert len(result) == 2

    def test_write_tag(self, client):
        result = client.write_tag("[default]Conveyors/Line1/Speed", 1800)
        assert result["written"] is True
        assert result["quality"] == "Good"

    def test_execute_script(self, client):
        result = client.execute_script("system.tag.readBlocking(['[default]test'])")
        assert result["result"] == "script executed"

    def test_query_history(self, client):
        result = client.query_history(
            "[default]Conveyors/Line1/Speed",
            "2026-04-12T00:00:00Z",
            "2026-04-12T12:00:00Z",
        )
        assert len(result["data"]) == 2
        assert result["data"][0]["value"] == 1700.0


# ── MCP tool wrappers ──────────────────────────────────────


class TestLiveTools:
    def test_read_tag_tool(self, mock_gateway):
        from ignition_mcp_server import server
        server._gateway = GatewayClient(mock_gateway)
        result = json.loads(server.read_tag("[default]Conveyors/Line1/Speed"))
        assert result[0]["value"] == 1750.5

    def test_read_tag_multiple(self, mock_gateway):
        from ignition_mcp_server import server
        server._gateway = GatewayClient(mock_gateway)
        result = json.loads(server.read_tag(
            "[default]Conveyors/Line1/Speed, [default]Conveyors/Line1/Running"
        ))
        assert len(result) == 2

    def test_write_tag_tool(self, mock_gateway):
        from ignition_mcp_server import server
        server._gateway = GatewayClient(mock_gateway)
        result = json.loads(server.write_tag("[default]Conveyors/Line1/Speed", "1800"))
        assert result["written"] is True

    def test_write_tag_bool_coercion(self, mock_gateway):
        from ignition_mcp_server import server
        server._gateway = GatewayClient(mock_gateway)
        result = json.loads(server.write_tag("[default]Conveyors/Line1/Running", "true"))
        assert result["written"] is True

    def test_execute_script_tool(self, mock_gateway):
        from ignition_mcp_server import server
        server._gateway = GatewayClient(mock_gateway)
        result = json.loads(server.execute_script("x = 1 + 1"))
        assert "result" in result

    def test_get_history_tool(self, mock_gateway):
        from ignition_mcp_server import server
        server._gateway = GatewayClient(mock_gateway)
        result = json.loads(server.get_history(
            "[default]Conveyors/Line1/Speed",
            "2026-04-12T00:00:00Z",
            "2026-04-12T12:00:00Z",
        ))
        assert len(result["data"]) == 2

    def test_no_gateway_raises(self):
        from ignition_mcp_server import server
        server._gateway = None
        result = json.loads(server.read_tag("[default]test"))
        assert "error" in result
        assert "No gateway configured" in result["error"]

    def test_configure_gateway(self, mock_gateway):
        from ignition_mcp_server.server import configure_gateway, _require_gateway
        configure_gateway(mock_gateway)
        gw = _require_gateway()
        assert gw.base_url == mock_gateway
