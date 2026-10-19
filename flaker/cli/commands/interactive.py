"""Interactive stack and command selector for Flaker."""

import sys
from pathlib import Path

from flaker.core.models import Role
from flaker.ui import ui


def run_interactive_mode(
    roles_db: dict[str, Role],
    aliases: dict[str, str],
    current_dir: Path,
    project_root: Path,
) -> tuple[str, list[str], dict[str, str]]:
    """Interactive role and command selector using arrow/spacebar menus."""
    is_subfolder = (project_root != current_dir) and (
        project_root / "flake.nix"
    ).exists()
    has_root_flake = (project_root / "flake.nix").exists()

    if is_subfolder:
        try:
            rel = current_dir.relative_to(project_root)
        except ValueError:
            rel = current_dir.name
        ui.info(f"Existing workspace detected at {ui.bold(str(project_root))}")
        cmd_options = [
            ("new", f"Add starter file in ./{rel}/", "Starter file in current directory"),
            ("shell", "Add flake.nix and .envrc", "DevShell at project root"),
            ("project", "Add project configs", "Root configs (pyproject.toml, etc.)"),
            ("init", "Create full setup", "Full workspace setup at project root"),
        ]
    elif has_root_flake:
        ui.info(f"Active workspace detected at {ui.bold(str(project_root))}")
        cmd_options = [
            ("new", "Add starter file", "Starter file in current directory"),
            ("shell", "Add flake.nix and .envrc", "DevShell at root"),
            ("project", "Add project configs", "Root configs (pyproject.toml, etc.)"),
            (
                "init",
                "Create full setup",
                "Full workspace setup (flake, envrc, configs, starter)",
            ),
        ]
    else:
        cmd_options = [
            ("init", "Create full setup", "Flake, envrc, project configs, starter"),
            ("shell", "Add flake.nix and .envrc", "DevShell environment only"),
            ("project", "Add project configs", "Root configs (pyproject.toml, etc.)"),
            ("new", "Add starter file", "Starter file in current directory"),
        ]

    chosen_cmd = ui.select("Action:", cmd_options)

    sorted_roles = sorted(roles_db.keys())
    role_options = [
        (r, f"{r:<10} [{roles_db[r].category}]", roles_db[r].description)
        for r in sorted_roles
    ]

    if chosen_cmd == "new":
        chosen_role = ui.select("Select role:", role_options)
        chosen_roles = [chosen_role]
    else:
        chosen_roles = ui.multiselect("Select roles:", role_options)
        if not chosen_roles:
            ui.warn("No roles selected. Exiting.")
            sys.exit(0)

    role_targets: dict[str, str] = {}
    if chosen_cmd != "shell":
        for r in chosen_roles:
            if r in roles_db and roles_db[r].targets:
                role_def = roles_db[r]
                options = [
                    (
                        t_key,
                        f"{t_key.capitalize():<8} - {t_meta.get('description', '')}",
                        "",
                    )
                    for t_key, t_meta in role_def.targets.items()
                ]
                chosen_target = ui.select(f"Select template for {r}:", options)
                role_targets[r] = chosen_target

    return chosen_cmd, chosen_roles, role_targets
