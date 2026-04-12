"""Named query parser — read Ignition SQL named query definitions."""

from __future__ import annotations

from typing import Any

from ignition_mcp_server.project_source import ProjectSource

MODULE_ID = "com.inductiveautomation.named-query"
TYPE_ID = "named-queries"


def list_named_queries(source: ProjectSource) -> list[str]:
    """Return all named query names in the project."""
    return source.list_resources(MODULE_ID, TYPE_ID)


def get_named_query(source: ProjectSource, query_name: str) -> dict[str, Any]:
    """Parse a named query and return its definition."""
    base = f"{MODULE_ID}/{TYPE_ID}/{query_name}"
    data = source.read_json(f"{base}/query.json")

    result: dict[str, Any] = {
        "name": query_name,
        "database": data.get("database", ""),
        "queryType": data.get("queryType", "Query"),
        "query": data.get("query", ""),
    }

    if data.get("parameters"):
        result["parameters"] = data["parameters"]
    if data.get("description"):
        result["description"] = data["description"]

    return result
