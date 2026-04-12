"""Script parser — discover and read Ignition project scripts."""

from __future__ import annotations

from typing import Any

from ignition_mcp_server.project_source import ProjectSource

# Known script locations in Ignition projects
_SCRIPT_LOCATIONS = [
    ("ignition", "script-python"),
    ("com.inductiveautomation.perspective", "general-props"),
]


def list_scripts(source: ProjectSource) -> list[dict[str, str]]:
    """Return all script resource paths with their scope."""
    results: list[dict[str, str]] = []
    for module_id, type_id in _SCRIPT_LOCATIONS:
        for path in source.list_resources(module_id, type_id):
            # Determine scope from resource.json if available
            scope = "project"
            try:
                rj = source.read_json(f"{module_id}/{type_id}/{path}/resource.json")
                scope_code = rj.get("scope", "A")
                scope = {"G": "gateway", "C": "client", "A": "all"}.get(scope_code, scope_code)
            except (FileNotFoundError, KeyError):
                pass
            results.append({"path": f"{module_id}/{type_id}/{path}", "name": path.split("/")[-1] if path else type_id, "scope": scope})
    return results


def get_script(source: ProjectSource, script_path: str) -> dict[str, Any]:
    """Read a script's source code by its resource path."""
    # Try code.py first, then fall back to other .py files
    try:
        code = source.read_resource(f"{script_path}/code.py").decode("utf-8")
    except (FileNotFoundError, KeyError):
        code = ""
        # Search for any .py file in the resource
        try:
            rj = source.read_json(f"{script_path}/resource.json")
            for f in rj.get("files", []):
                if f.endswith(".py"):
                    code = source.read_resource(f"{script_path}/{f}").decode("utf-8")
                    break
        except (FileNotFoundError, KeyError):
            pass

    return {"path": script_path, "code": code}
