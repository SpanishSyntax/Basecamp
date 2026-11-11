"""Domain models and data definitions for Basecamp."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Role:
    """Definition of a development stack role."""

    pkgs: list[str]
    hooks: list[str]
    category: str = "General"
    description: str = ""
    ignores: list[str] = field(default_factory=list)
    targets: dict[str, dict[str, Any]] = field(default_factory=dict)
    icon: str = "⛺"
    display_name: str = ""
    status_detail: str = ""
