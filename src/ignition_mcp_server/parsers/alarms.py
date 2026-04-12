"""Alarm pipeline parser — read Ignition alarm notification configurations."""

from __future__ import annotations

from typing import Any

from ignition_mcp_server.project_source import ProjectSource

MODULE_ID = "com.inductiveautomation.alarm-notification"
TYPE_ID = "alarm-pipelines"


def list_alarms(source: ProjectSource) -> list[str]:
    """Return all alarm pipeline names in the project."""
    return source.list_resources(MODULE_ID, TYPE_ID)


def get_alarm(source: ProjectSource, pipeline_name: str) -> dict[str, Any]:
    """Parse an alarm pipeline and return its configuration."""
    base = f"{MODULE_ID}/{TYPE_ID}/{pipeline_name}"

    # Determine the data file from resource.json
    try:
        rj = source.read_json(f"{base}/resource.json")
        data_file = rj.get("files", ["alarm-config.json"])[0]
    except (FileNotFoundError, KeyError):
        data_file = "alarm-config.json"

    data = source.read_json(f"{base}/{data_file}")

    result: dict[str, Any] = {
        "name": data.get("name", pipeline_name),
        "enabled": data.get("enabled", True),
    }

    stages = data.get("stages", [])
    if stages:
        result["stages"] = [
            {
                "name": s.get("name", ""),
                "type": s.get("type", "unknown"),
                **({k: v for k, v in s.get("config", {}).items()} if s.get("config") else {}),
                **({"transitionCount": len(s["transitions"])} if s.get("transitions") else {}),
            }
            for s in stages
        ]

    return result
