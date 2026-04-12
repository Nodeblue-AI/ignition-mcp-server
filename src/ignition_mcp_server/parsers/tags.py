"""Tag parser — read Ignition tag JSON exports."""

from __future__ import annotations

from typing import Any

from ignition_mcp_server.project_source import ProjectSource


def parse_tags(
    source: ProjectSource, tag_path: str = "", provider: str = "default"
) -> list[dict[str, Any]]:
    """Parse tags from the project, optionally filtered by path.

    Args:
        source: Project source to read from.
        tag_path: Optional folder path to filter (e.g. "Conveyors/Line1").
        provider: Tag provider name (default: "default"). Use list_tag_providers() to discover.
    """
    try:
        data = source.read_json(f"tags/{provider}/tags.json")
    except (FileNotFoundError, KeyError):
        return []

    tags = data.get("tags", data) if isinstance(data, dict) else data
    if not isinstance(tags, list):
        return []

    if not tag_path:
        return _summarize_tags(tags)

    # Walk path segments to find the target folder
    parts = [p for p in tag_path.strip("/").split("/") if p]
    current = tags
    for part in parts:
        found = None
        for tag in current:
            if tag.get("name") == part and tag.get("tagType") == "Folder":
                found = tag.get("tags", [])
                break
        if found is None:
            return []
        current = found

    return _summarize_tags(current)


def list_tag_providers(source: ProjectSource) -> list[str]:
    """Return all tag provider names found in the project."""
    providers: list[str] = []
    # Directory source: look for tags/*/tags.json
    # Zip source: look for <prefix>tags/*/tags.json
    # Use list_resources pattern — check for known structure
    try:
        # Try reading the tags directory listing via resource enumeration
        # Both source types support read_resource, so probe common providers
        for candidate in _discover_providers(source):
            providers.append(candidate)
    except Exception:
        pass
    if not providers:
        # Fallback: check if default exists
        try:
            source.read_json("tags/default/tags.json")
            providers.append("default")
        except (FileNotFoundError, KeyError):
            pass
    return sorted(providers)


def _discover_providers(source: ProjectSource) -> list[str]:
    """Discover tag providers by inspecting the project structure."""
    from ignition_mcp_server.project_source import DirectoryProjectSource, ZipProjectSource

    providers: list[str] = []
    if isinstance(source, DirectoryProjectSource):
        tags_dir = source._root / "tags"
        if tags_dir.is_dir():
            for child in tags_dir.iterdir():
                if child.is_dir() and (child / "tags.json").exists():
                    providers.append(child.name)
    elif isinstance(source, ZipProjectSource):
        import re
        pattern = re.compile(re.escape(source._prefix) + r"tags/([^/]+)/tags\.json$")
        for name in source._zf.namelist():
            m = pattern.match(name)
            if m:
                providers.append(m.group(1))
    return providers


def _summarize_tags(tags: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return a compact summary of each tag."""
    results = []
    for tag in tags:
        entry: dict[str, Any] = {"name": tag["name"], "tagType": tag.get("tagType", "AtomicTag")}
        if entry["tagType"] == "Folder":
            entry["childCount"] = len(tag.get("tags", []))
        else:
            for key in ("dataType", "valueSource", "value", "documentation", "typeId"):
                if key in tag:
                    entry[key] = tag[key]
        results.append(entry)
    return results
