"""Perspective view parser."""

from __future__ import annotations

from typing import Any

from ignition_mcp_server.project_source import ProjectSource

MODULE_ID = "com.inductiveautomation.perspective"
TYPE_ID = "views"


def list_views(source: ProjectSource) -> list[str]:
    """Return all Perspective view paths in the project."""
    return source.list_resources(MODULE_ID, TYPE_ID)


def get_view(source: ProjectSource, view_path: str) -> dict[str, Any]:
    """Parse a Perspective view and return its structure."""
    resource_base = f"{MODULE_ID}/{TYPE_ID}/{view_path}"
    view_data = source.read_json(f"{resource_base}/view.json")
    return {
        "path": view_path,
        "root": _summarize_component(view_data.get("root", {})),
    }


def _summarize_component(comp: dict[str, Any]) -> dict[str, Any]:
    """Recursively summarize a component tree."""
    summary: dict[str, Any] = {"type": comp.get("type", "unknown")}
    if comp.get("meta", {}).get("name"):
        summary["name"] = comp["meta"]["name"]

    # Extract bindings
    props = comp.get("props", {})
    if props:
        summary["props"] = props

    # Count bindings in propConfig
    prop_config = comp.get("propConfig", {})
    bindings = _extract_bindings(prop_config)
    if bindings:
        summary["bindings"] = bindings

    # Events
    events = comp.get("events", {})
    if events:
        summary["eventCount"] = sum(len(v) if isinstance(v, list) else 1 for v in events.values())

    # Recurse children
    children = comp.get("children", [])
    if children:
        summary["children"] = [_summarize_component(c) for c in children]

    return summary


def _extract_bindings(prop_config: dict[str, Any], prefix: str = "") -> list[dict[str, str]]:
    """Extract binding definitions from propConfig."""
    bindings: list[dict[str, str]] = []
    for key, val in prop_config.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(val, dict):
            if "binding" in val:
                b = val["binding"]
                bindings.append({"property": path, "type": b.get("type", "unknown")})
            else:
                bindings.extend(_extract_bindings(val, path))
    return bindings
