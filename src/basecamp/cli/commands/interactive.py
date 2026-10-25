"""Interactive stack and command selector for Basecamp."""

import sys
from pathlib import Path

from basecamp import __version__
from basecamp.cli.commands.active import detect_active_roles
from basecamp.core.models import Role
from basecamp.ui import ui


def run_interactive_mode(
    roles_db: dict[str, Role],
    aliases: dict[str, str],
    current_dir: Path,
    project_root: Path,
) -> tuple[str, list[str], dict[str, str]]:
    """Interactive role and command selector using arrow/spacebar menus."""
    flake_path = project_root / "flake.nix"
    has_root_flake = flake_path.exists()
    is_subfolder = (project_root != current_dir) and has_root_flake

    active_roles_summary = ""
    if has_root_flake:
        try:
            content = flake_path.read_text(encoding="utf-8")
            diags, _, _ = detect_active_roles(content, roles_db, aliases)
            if diags:
                active_roles_summary = ", ".join(d.role_key for d in diags)
        except OSError:
            pass

    ws_status = (
        ui.green(f"active ({active_roles_summary})" if active_roles_summary else "active (flake.nix)")
        if has_root_flake
        else ui.yellow("uninitialized")
    )
    categories = sorted(set(r.category for r in roles_db.values()))
    cat_summary = ", ".join(categories[:4])
    if len(categories) > 4:
        cat_summary += f", +{len(categories) - 4} more"

    panel_lines = [
        f"{ui.bold('Basecamp Version:')}   {ui.bold_cyan(f'v{__version__}')} (Scaffolding & DevShell Engine)",
        f"{ui.bold('Active Project:')}    {project_root} ({ws_status})",
        f"{ui.bold('Working Directory:')} {current_dir}",
        f"{ui.bold('Registered Roles:')}  {len(roles_db)} roles ({cat_summary})",
    ]
    ui.panel("BASECAMP REPRODUCIBLE NIX WORKSPACE ENGINE", panel_lines)

    if is_subfolder:
        try:
            rel = current_dir.relative_to(project_root)
        except ValueError:
            rel = current_dir.name
        cmd_options = [
            ("new", f"Add starter file in ./{rel}/", "Starter file in current directory"),
            ("shell", "Add flake.nix and .envrc", "DevShell at project root"),
            ("project", "Add project configs", "Root configs (pyproject.toml, etc.)"),
            ("init", "Create full setup", "Full workspace setup at project root"),
        ]
    elif has_root_flake:
        ui.info(f"Active workspace detected at {ui.bold(str(project_root))}")
        cmd_options = [
            ("active", "Diagnose active roles", "List active roles, channel & packages in flake.nix"),
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

    if chosen_cmd == "active":
        return "active", [], {}

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
