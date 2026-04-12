"""Project source abstraction — read Ignition projects from .zip or directory."""

from __future__ import annotations

import json
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path, PurePosixPath
from typing import Any


class ProjectSource(ABC):
    """Abstract interface for reading Ignition project files."""

    @abstractmethod
    def project_info(self) -> dict[str, Any]:
        """Return parsed project.json contents."""

    @abstractmethod
    def list_resources(self, module_id: str, type_id: str) -> list[str]:
        """List resource paths under <module_id>/<type_id>/."""

    @abstractmethod
    def read_resource(self, resource_path: str) -> bytes:
        """Read a file by its path relative to the project root."""

    def read_json(self, resource_path: str) -> Any:
        return json.loads(self.read_resource(resource_path))


class DirectoryProjectSource(ProjectSource):
    def __init__(self, path: Path) -> None:
        self._root = path

    def project_info(self) -> dict[str, Any]:
        return json.loads((self._root / "project.json").read_bytes())

    def list_resources(self, module_id: str, type_id: str) -> list[str]:
        base = self._root / module_id / type_id
        if not base.is_dir():
            return []
        results: list[str] = []
        for rj in base.rglob("resource.json"):
            rel = rj.parent.relative_to(base)
            results.append(str(rel) if str(rel) != "." else "")
        return sorted(results)

    def read_resource(self, resource_path: str) -> bytes:
        return (self._root / resource_path).read_bytes()


class ZipProjectSource(ProjectSource):
    def __init__(self, path: Path) -> None:
        self._zf = zipfile.ZipFile(path, "r")
        # Detect project root inside zip (may be nested one level)
        self._prefix = ""
        for name in self._zf.namelist():
            if name.endswith("project.json"):
                self._prefix = name[: -len("project.json")]
                break

    def project_info(self) -> dict[str, Any]:
        return json.loads(self._zf.read(self._prefix + "project.json"))

    def list_resources(self, module_id: str, type_id: str) -> list[str]:
        base = self._prefix + module_id + "/" + type_id + "/"
        results: list[str] = []
        for name in self._zf.namelist():
            if name.startswith(base) and name.endswith("resource.json"):
                rel = name[len(base) : -len("/resource.json")]
                results.append(rel)
        return sorted(results)

    def read_resource(self, resource_path: str) -> bytes:
        return self._zf.read(self._prefix + resource_path)

    def close(self) -> None:
        self._zf.close()


def open_project(path: str) -> ProjectSource:
    """Open an Ignition project from a .zip file or directory path."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Project path not found: {path}")
    if p.is_file() and p.suffix == ".zip":
        return ZipProjectSource(p)
    if p.is_dir():
        if not (p / "project.json").exists():
            raise FileNotFoundError(f"No project.json found in {path}")
        return DirectoryProjectSource(p)
    raise ValueError(f"Path must be a .zip file or directory: {path}")
