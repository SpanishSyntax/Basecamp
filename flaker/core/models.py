"""Domain models and data definitions for Flaker."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TargetSpec:
    """Specification for a role sub-target / document template."""

    project: list[str] = field(default_factory=list)
    starter: list[str] = field(default_factory=list)
    description: str = ""
    aliases: list[str] = field(default_factory=list)


@dataclass
class Role:
    """Definition of a development stack role."""

    pkgs: list[str]
    hooks: list[str]
    category: str = "General"
    description: str = ""
    ignores: list[str] = field(default_factory=list)
    targets: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass
class PackageBundle:
    """Definition of an optional or default package bundle (Typst/LaTeX)."""

    id: str
    label: str
    desc: str
    snippet: str
    default: bool = False
