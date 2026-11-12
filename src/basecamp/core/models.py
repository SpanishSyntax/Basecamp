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
    # Packages sourced from the `nixpkgs-unstable` input instead of stable.
    unstable_pkgs: list[str] = field(default_factory=list)

    def channel_pkgs(self) -> tuple[list[str], list[str]]:
        """Returns (stable, unstable) package attrs, honouring `unstable.` prefixes."""
        stable: list[str] = []
        unstable: list[str] = list(self.unstable_pkgs)
        for pkg in self.pkgs:
            if pkg.startswith("unstable."):
                unstable.append(pkg[len("unstable.") :])
            else:
                stable.append(pkg)
        return stable, unstable

    @property
    def all_pkgs(self) -> list[str]:
        """All package attrs regardless of channel."""
        stable, unstable = self.channel_pkgs()
        return stable + unstable
