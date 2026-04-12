"""Ignition MCP Server — FastMCP server exposing Ignition project tools."""

from __future__ import annotations

import json
from typing import Any

from fastmcp import FastMCP

from ignition_mcp_server.gateway_client import GatewayClient
from ignition_mcp_server.parsers import alarms, named_queries, scripts, tags, udts, views
from ignition_mcp_server.project_source import open_project

# Set by CLI when --gateway-url is provided
_gateway: GatewayClient | None = None


def configure_gateway(url: str, username: str = "", password: str = "") -> None:
    """Configure the live gateway connection."""
    global _gateway
    _gateway = GatewayClient(url, username, password)


def _require_gateway() -> GatewayClient:
    if _gateway is None:
        raise RuntimeError(
            "No gateway configured. Start the server with --gateway-url to enable live tools."
        )
    return _gateway


def _error(msg: str) -> str:
    return json.dumps({"error": msg})


mcp = FastMCP(
    "Ignition MCP Server",
    instructions=(
        "This server provides access to Ignition SCADA projects and gateways. "
        "Use project tools to explore tags, views, scripts, UDTs, alarms, and named queries "
        "from project files (provide project_path). "
        "Use live tools (read_tag, write_tag, execute_script, get_history) to interact "
        "with a running Ignition gateway (requires --gateway-url at startup)."
    ),
)


@mcp.tool
def ping() -> str:
    """Health check — verify the server is running."""
    return "pong"


@mcp.tool
def get_tags(project_path: str, tag_path: str = "", provider: str = "default") -> str:
    """Get tags from an Ignition project, optionally filtered by folder path.

    Args:
        project_path: Path to Ignition project directory or .zip export.
        tag_path: Optional folder path to filter (e.g. "Conveyors/Line1").
        provider: Tag provider name (default: "default"). Use list_tag_providers to discover.
    """
    try:
        source = open_project(project_path)
        result = tags.parse_tags(source, tag_path, provider)
        return json.dumps(result, indent=2)
    except FileNotFoundError as e:
        return _error(str(e))
    except Exception as e:
        return _error(f"Failed to read tags: {e}")


@mcp.tool
def list_tag_providers(project_path: str) -> str:
    """List all tag provider names in an Ignition project (e.g. 'default', 'edge').

    Args:
        project_path: Path to Ignition project directory or .zip export.
    """
    try:
        source = open_project(project_path)
        result = tags.list_tag_providers(source)
        return json.dumps(result, indent=2)
    except FileNotFoundError as e:
        return _error(str(e))
    except Exception as e:
        return _error(f"Failed to list tag providers: {e}")


@mcp.tool
def list_views(project_path: str) -> str:
    """List all Perspective view paths in an Ignition project.

    Args:
        project_path: Path to Ignition project directory or .zip export.
    """
    try:
        source = open_project(project_path)
        return json.dumps(views.list_views(source), indent=2)
    except FileNotFoundError as e:
        return _error(str(e))
    except Exception as e:
        return _error(f"Failed to list views: {e}")


@mcp.tool
def get_view(project_path: str, view_path: str) -> str:
    """Get a Perspective view's component tree, bindings, and structure.

    Args:
        project_path: Path to Ignition project directory or .zip export.
        view_path: View path (e.g. "Overview" or "Screens/MotorDetail").
    """
    try:
        source = open_project(project_path)
        result = views.get_view(source, view_path)
        return json.dumps(result, indent=2)
    except FileNotFoundError as e:
        return _error(str(e))
    except Exception as e:
        return _error(f"Failed to read view '{view_path}': {e}")


@mcp.tool
def list_scripts(project_path: str) -> str:
    """List all scripts in an Ignition project with their scope.

    Args:
        project_path: Path to Ignition project directory or .zip export.
    """
    try:
        source = open_project(project_path)
        return json.dumps(scripts.list_scripts(source), indent=2)
    except FileNotFoundError as e:
        return _error(str(e))
    except Exception as e:
        return _error(f"Failed to list scripts: {e}")


@mcp.tool
def get_script(project_path: str, script_path: str) -> str:
    """Get the source code of an Ignition project script.

    Args:
        project_path: Path to Ignition project directory or .zip export.
        script_path: Script resource path (from list_scripts output).
    """
    try:
        source = open_project(project_path)
        result = scripts.get_script(source, script_path)
        return json.dumps(result, indent=2)
    except FileNotFoundError as e:
        return _error(str(e))
    except Exception as e:
        return _error(f"Failed to read script '{script_path}': {e}")


@mcp.tool
def list_udts(project_path: str) -> str:
    """List all UDT (User Defined Type) names in an Ignition project.

    Args:
        project_path: Path to Ignition project directory or .zip export.
    """
    try:
        source = open_project(project_path)
        return json.dumps(udts.list_udts(source), indent=2)
    except FileNotFoundError as e:
        return _error(str(e))
    except Exception as e:
        return _error(f"Failed to list UDTs: {e}")


@mcp.tool
def get_udt(project_path: str, udt_name: str = "") -> str:
    """Get UDT definition(s) with member details.

    Args:
        project_path: Path to Ignition project directory or .zip export.
        udt_name: Optional UDT name. If empty, returns all UDTs.
    """
    try:
        source = open_project(project_path)
        result = udts.get_udt(source, udt_name or None)
        return json.dumps(result, indent=2)
    except FileNotFoundError as e:
        return _error(str(e))
    except Exception as e:
        return _error(f"Failed to read UDT: {e}")


@mcp.tool
def list_alarms(project_path: str) -> str:
    """List all alarm pipeline names in an Ignition project.

    Args:
        project_path: Path to Ignition project directory or .zip export.
    """
    try:
        source = open_project(project_path)
        return json.dumps(alarms.list_alarms(source), indent=2)
    except FileNotFoundError as e:
        return _error(str(e))
    except Exception as e:
        return _error(f"Failed to list alarms: {e}")


@mcp.tool
def get_alarm(project_path: str, pipeline_name: str) -> str:
    """Get an alarm pipeline's configuration including stages, notifications, and transitions.

    Args:
        project_path: Path to Ignition project directory or .zip export.
        pipeline_name: Alarm pipeline name (from list_alarms output).
    """
    try:
        source = open_project(project_path)
        result = alarms.get_alarm(source, pipeline_name)
        return json.dumps(result, indent=2)
    except FileNotFoundError as e:
        return _error(str(e))
    except Exception as e:
        return _error(f"Failed to read alarm pipeline '{pipeline_name}': {e}")


@mcp.tool
def list_named_queries(project_path: str) -> str:
    """List all named query names in an Ignition project.

    Args:
        project_path: Path to Ignition project directory or .zip export.
    """
    try:
        source = open_project(project_path)
        return json.dumps(named_queries.list_named_queries(source), indent=2)
    except FileNotFoundError as e:
        return _error(str(e))
    except Exception as e:
        return _error(f"Failed to list named queries: {e}")


@mcp.tool
def get_named_query(project_path: str, query_name: str) -> str:
    """Get a named query's SQL, parameters, database connection, and type.

    Args:
        project_path: Path to Ignition project directory or .zip export.
        query_name: Named query name (from list_named_queries output).
    """
    try:
        source = open_project(project_path)
        result = named_queries.get_named_query(source, query_name)
        return json.dumps(result, indent=2)
    except FileNotFoundError as e:
        return _error(str(e))
    except Exception as e:
        return _error(f"Failed to read named query '{query_name}': {e}")


# ── Live Gateway Tools ──────────────────────────────────────


@mcp.tool
def read_tag(tag_path: str) -> str:
    """Read the current value of one or more tags from a live Ignition gateway.

    Requires the server to be started with --gateway-url pointing to an Ignition
    gateway with the WebDev module installed.

    Args:
        tag_path: Tag path(s), comma-separated for multiple (e.g. "[default]Conveyors/Line1/Speed").
    """
    try:
        gw = _require_gateway()
        paths = [p.strip() for p in tag_path.split(",")]
        result = gw.read_tags(paths)
        return json.dumps(result, indent=2)
    except RuntimeError as e:
        return _error(str(e))
    except Exception as e:
        return _error(f"Failed to read tag(s): {e}")


@mcp.tool
def write_tag(tag_path: str, value: str) -> str:
    """Write a value to a tag on a live Ignition gateway.

    Requires the server to be started with --gateway-url. The value is sent as-is;
    the gateway handles type coercion.

    Args:
        tag_path: Full tag path (e.g. "[default]Conveyors/Line1/Speed").
        value: Value to write (string representation — gateway coerces to tag data type).
    """
    try:
        gw = _require_gateway()
        # Attempt numeric coercion for common cases
        coerced: Any = value
        if value.lower() in ("true", "false"):
            coerced = value.lower() == "true"
        else:
            try:
                coerced = int(value)
            except ValueError:
                try:
                    coerced = float(value)
                except ValueError:
                    pass
        result = gw.write_tag(tag_path, coerced)
        return json.dumps(result, indent=2)
    except RuntimeError as e:
        return _error(str(e))
    except Exception as e:
        return _error(f"Failed to write tag '{tag_path}': {e}")


@mcp.tool
def execute_script(code: str) -> str:
    """Execute a Python script on the Ignition gateway and return the result.

    Requires the server to be started with --gateway-url. The script runs in
    gateway scope with access to system.* functions.

    Args:
        code: Python code to execute on the gateway.
    """
    try:
        gw = _require_gateway()
        result = gw.execute_script(code)
        return json.dumps(result, indent=2)
    except RuntimeError as e:
        return _error(str(e))
    except Exception as e:
        return _error(f"Failed to execute script: {e}")


@mcp.tool
def get_history(tag_path: str, start: str, end: str) -> str:
    """Query historical tag data from a live Ignition gateway.

    Requires the server to be started with --gateway-url and a historian
    configured on the gateway.

    Args:
        tag_path: Full tag path (e.g. "[default]Conveyors/Line1/Speed").
        start: Start time as ISO 8601 (e.g. "2026-04-12T00:00:00Z").
        end: End time as ISO 8601 (e.g. "2026-04-12T12:00:00Z").
    """
    try:
        gw = _require_gateway()
        result = gw.query_history(tag_path, start, end)
        return json.dumps(result, indent=2)
    except RuntimeError as e:
        return _error(str(e))
    except Exception as e:
        return _error(f"Failed to query history: {e}")
