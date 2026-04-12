"""Tag parser — read Ignition tag JSON exports."""

from __future__ import annotations

from typing import Any

from ignition_mcp_server.project_source import ProjectSource


def parse_tags(source: ProjectSource, tag_path: str = "") -> list[dict[str, Any]]:
    """Parse tags from the project, optionally filtered by path."""
    try:
        data = source.read_json("tags/default/tags.json")
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
