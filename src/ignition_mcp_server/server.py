"""Ignition MCP Server — FastMCP server exposing Ignition project tools."""

from __future__ import annotations

import json
from typing import Any

from fastmcp import FastMCP

from ignition_mcp_server.parsers import alarms, named_queries, scripts, tags, udts, views
from ignition_mcp_server.project_source import open_project

mcp = FastMCP(
    "Ignition MCP Server",
    instructions=(
        "This server provides read-only access to Ignition SCADA projects. "
        "Use it to explore tags, Perspective views, scripts, UDT definitions, "
        "alarm pipelines, and named queries. "
        "Provide a project_path pointing to an Ignition project directory or .zip export."
    ),
)


@mcp.tool
def ping() -> str:
    """Health check — verify the server is running."""
    return "pong"


@mcp.tool
def get_tags(project_path: str, tag_path: str = "") -> str:
    """Get tags from an Ignition project, optionally filtered by folder path.

    Args:
        project_path: Path to Ignition project directory or .zip export.
        tag_path: Optional folder path to filter (e.g. "Conveyors/Line1").
    """
    source = open_project(project_path)
    result = tags.parse_tags(source, tag_path)
    return json.dumps(result, indent=2)


@mcp.tool
def list_views(project_path: str) -> str:
    """List all Perspective view paths in an Ignition project.

    Args:
        project_path: Path to Ignition project directory or .zip export.
    """
    source = open_project(project_path)
    return json.dumps(views.list_views(source), indent=2)


@mcp.tool
def get_view(project_path: str, view_path: str) -> str:
    """Get a Perspective view's component tree, bindings, and structure.

    Args:
        project_path: Path to Ignition project directory or .zip export.
        view_path: View path (e.g. "Overview" or "Screens/MotorDetail").
    """
    source = open_project(project_path)
    result = views.get_view(source, view_path)
    return json.dumps(result, indent=2)


@mcp.tool
def list_scripts(project_path: str) -> str:
    """List all scripts in an Ignition project with their scope.

    Args:
        project_path: Path to Ignition project directory or .zip export.
    """
    source = open_project(project_path)
    return json.dumps(scripts.list_scripts(source), indent=2)


@mcp.tool
def get_script(project_path: str, script_path: str) -> str:
    """Get the source code of an Ignition project script.

    Args:
        project_path: Path to Ignition project directory or .zip export.
        script_path: Script resource path (from list_scripts output).
    """
    source = open_project(project_path)
    result = scripts.get_script(source, script_path)
    return json.dumps(result, indent=2)


@mcp.tool
def list_udts(project_path: str) -> str:
    """List all UDT (User Defined Type) names in an Ignition project.

    Args:
        project_path: Path to Ignition project directory or .zip export.
    """
    source = open_project(project_path)
    return json.dumps(udts.list_udts(source), indent=2)


@mcp.tool
def get_udt(project_path: str, udt_name: str = "") -> str:
    """Get UDT definition(s) with member details.

    Args:
        project_path: Path to Ignition project directory or .zip export.
        udt_name: Optional UDT name. If empty, returns all UDTs.
    """
    source = open_project(project_path)
    result = udts.get_udt(source, udt_name or None)
    return json.dumps(result, indent=2)


@mcp.tool
def list_alarms(project_path: str) -> str:
    """List all alarm pipeline names in an Ignition project.

    Args:
        project_path: Path to Ignition project directory or .zip export.
    """
    source = open_project(project_path)
    return json.dumps(alarms.list_alarms(source), indent=2)


@mcp.tool
def get_alarm(project_path: str, pipeline_name: str) -> str:
    """Get an alarm pipeline's configuration including stages, notifications, and transitions.

    Args:
        project_path: Path to Ignition project directory or .zip export.
        pipeline_name: Alarm pipeline name (from list_alarms output).
    """
    source = open_project(project_path)
    result = alarms.get_alarm(source, pipeline_name)
    return json.dumps(result, indent=2)


@mcp.tool
def list_named_queries(project_path: str) -> str:
    """List all named query names in an Ignition project.

    Args:
        project_path: Path to Ignition project directory or .zip export.
    """
    source = open_project(project_path)
    return json.dumps(named_queries.list_named_queries(source), indent=2)


@mcp.tool
def get_named_query(project_path: str, query_name: str) -> str:
    """Get a named query's SQL, parameters, database connection, and type.

    Args:
        project_path: Path to Ignition project directory or .zip export.
        query_name: Named query name (from list_named_queries output).
    """
    source = open_project(project_path)
    result = named_queries.get_named_query(source, query_name)
    return json.dumps(result, indent=2)
