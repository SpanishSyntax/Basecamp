"""User configuration parser for Basecamp."""

import os
import tomllib
from pathlib import Path

from basecamp.core.models import Role
from basecamp.ui import ui


def load_user_config() -> tuple[dict[str, Role], dict[str, str], list[Path]]:
    """Loads custom roles, aliases, and templates from ~/.config/basecamp/roles.toml."""
    xdg_base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    config_dir = xdg_base / "basecamp"
    roles_file = config_dir / "roles.toml"

    extra_roles: dict[str, Role] = {}
    extra_aliases: dict[str, str] = {}
    custom_asset_dirs: list[Path] = [config_dir / "templates"]

    if roles_file.exists():
        try:
            with open(roles_file, "rb") as f:
                data = tomllib.load(f)
            for role_key, role_data in data.get("roles", {}).items():
                extra_roles[role_key] = Role(
                    pkgs=role_data.get("pkgs", []),
                    hooks=role_data.get("hooks", []),
                    category=role_data.get("category", "Custom"),
                    description=role_data.get("description", "Custom user role"),
                    ignores=role_data.get("ignores", []),
                    targets=role_data.get("targets", {}),
                )
            for alias_key, target_role in data.get("aliases", {}).items():
                extra_aliases[alias_key] = target_role
        except Exception as e:
            ui.warn(f"Failed to parse user config at {roles_file}: {e}")

    return extra_roles, extra_aliases, custom_asset_dirs
