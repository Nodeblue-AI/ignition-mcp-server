"""UDT parser — extract User Defined Type definitions from tag exports."""

from __future__ import annotations

from typing import Any

from ignition_mcp_server.project_source import ProjectSource


def list_udts(source: ProjectSource) -> list[str]:
    """Return names of all UDT definitions in the project."""
    tags = _load_all_tags(source)
    return sorted(t["name"] for t in tags if t.get("tagType") == "UdtType")


def get_udt(source: ProjectSource, udt_name: str | None = None) -> list[dict[str, Any]]:
    """Return UDT definition(s). If udt_name is None, return all."""
    tags = _load_all_tags(source)
    udts = [t for t in tags if t.get("tagType") == "UdtType"]
    if udt_name:
        udts = [t for t in udts if t["name"] == udt_name]

    return [_summarize_udt(u) for u in udts]


def _summarize_udt(udt: dict[str, Any]) -> dict[str, Any]:
    """Produce a compact summary of a UDT definition."""
    members = []
    for tag in udt.get("tags", []):
        member: dict[str, Any] = {"name": tag["name"], "tagType": tag.get("tagType", "AtomicTag")}
        for key in ("dataType", "value", "documentation", "valueSource"):
            if key in tag:
                member[key] = tag[key]
        members.append(member)

    result: dict[str, Any] = {"name": udt["name"], "members": members}
    if "parameters" in udt:
        result["parameters"] = udt["parameters"]
    if "documentation" in udt:
        result["documentation"] = udt["documentation"]
    return result


def _load_all_tags(source: ProjectSource) -> list[dict[str, Any]]:
    """Load the flat top-level tag list from the default provider."""
    try:
        data = source.read_json("tags/default/tags.json")
    except (FileNotFoundError, KeyError):
        return []
    tags = data.get("tags", data) if isinstance(data, dict) else data
    return tags if isinstance(tags, list) else []
