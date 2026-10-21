"""Main command dispatcher and router for Flaker CLI."""

import os
import sys
from pathlib import Path

from flaker import __version__
from flaker.cli.args import handle_color_args, parse_cli_args, print_help
from flaker.cli.commands.active import display_active_roles
from flaker.cli.commands.info import display_role_info
from flaker.cli.commands.interactive import run_interactive_mode
from flaker.cli.commands.list_cmd import display_roles_list
from flaker.cli.resolver import (
    find_role_for_standalone_target,
    resolve_role_target,
)
from flaker.core.config import load_user_config
from flaker.core.environment import (
    find_project_root,
    get_project_name,
    prepare_flake_env,
)
from flaker.core.registry import (
    BUILTIN_ALIASES,
    build_builtin_role_registry,
    resolve_nixpkgs_url,
)
from flaker.scaffold.engine import resolve_document_metadata, scaffold_assets
from flaker.scaffold.manifests import configure_packages_interactive
from flaker.ui import ui


def main() -> None:
    """Main CLI entry point."""
    handle_color_args(sys.argv[1:])

    # Basic flags
    if any(a in ("--help", "-h", "help") for a in sys.argv[1:]):
        print_help()
        sys.exit(0)

    if any(a in ("-V", "--version", "-v", "version") for a in sys.argv[1:]):
        print(f"{ui.badge()} {ui.bold(f'v{__version__}')}")
        sys.exit(0)

    # Smart Paths & Asset Discovery
    pkg_root = Path(__file__).resolve().parent.parent
    fallback_template = pkg_root / "flake.template"
    fallback_assets = pkg_root / "templates"
    default_runtime_libs = "stdenv.cc.cc.lib,zlib,glib,libxml2,openssl,libffi"

    template_path_env = os.environ.get("FLAKE_TEMPLATE")
    template_path = Path(template_path_env) if template_path_env else fallback_template

    assets_dir_env = os.environ.get("FLAKER_ASSETS")
    primary_assets_dir = Path(assets_dir_env) if assets_dir_env else fallback_assets

    libs_list = os.environ.get("LIBS_LIST", default_runtime_libs).replace(",", " ")

    # Load custom configuration from ~/.config/flaker/roles.toml
    user_roles, user_aliases, custom_asset_dirs = load_user_config()
    all_asset_dirs = custom_asset_dirs + [primary_assets_dir]

    current_dir = Path.cwd()
    project_root = find_project_root(current_dir)
    project_name = get_project_name(project_root)

    roles_db = build_builtin_role_registry(project_name)
    roles_db.update(user_roles)

    aliases = dict(BUILTIN_ALIASES)
    aliases.update(user_aliases)

    raw_args = sys.argv[1:]
    parsed = parse_cli_args(raw_args)
    filtered_args = parsed.filtered_args

    # Handle 'flaker active' / 'flaker status' / 'flaker -a'
    if parsed.active and not filtered_args:
        display_active_roles(project_root, roles_db, aliases)
        sys.exit(0)

    if filtered_args and filtered_args[0] in ("active", "status"):
        display_active_roles(project_root, roles_db, aliases)
        sys.exit(0)

    # Handle 'flaker list' / 'flaker list -a' / 'flaker list --active'
    if filtered_args and filtered_args[0] in ("list", "ls"):
        if parsed.active or any(a in ("-a", "--active") for a in raw_args):
            display_active_roles(project_root, roles_db, aliases)
            sys.exit(0)
        display_roles_list(roles_db, aliases)
        sys.exit(0)

    # Handle 'flaker info <role>'
    if filtered_args and filtered_args[0] in ("info", "show"):
        if len(filtered_args) < 2:
            ui.error("Missing role name for 'flaker info'. Example: flaker info python")
            sys.exit(1)
        display_role_info(filtered_args[1], roles_db, aliases, all_asset_dirs)
        sys.exit(0)

    COMMAND_ALIASES = {
        "starter": "new",
        "draft": "new",
        "scaffold": "new",
        "shell": "shell",
        "env": "shell",
        "flake": "shell",
        "base": "project",
        "root": "project",
        "packages": "packages",
        "package": "packages",
        "pkg": "packages",
        "status": "active",
        "active": "active",
    }

    command = ""
    resolved_roles: list[str] = []
    role_targets: dict[str, str] = {}
    unparsed_roles: list[str] = []

    # Interactive trigger if no arguments provided in a TTY
    if not filtered_args:
        if sys.stdin.isatty():
            command, resolved_roles, role_targets = run_interactive_mode(
                roles_db, aliases, current_dir, project_root
            )
        else:
            print_help()
            sys.exit(1)
    elif filtered_args[0] == "interactive":
        command, resolved_roles, role_targets = run_interactive_mode(
            roles_db, aliases, current_dir, project_root
        )
    else:
        command = COMMAND_ALIASES.get(filtered_args[0], filtered_args[0])
        unparsed_roles = filtered_args[1:]

        # If subcommand given without roles in a TTY (e.g. 'flaker new' or 'flaker init')
        if command in ("init", "new", "shell", "project") and not unparsed_roles:
            if sys.stdin.isatty():
                sorted_roles = sorted(roles_db.keys())
                role_options = [
                    (r, f"{r:<10} [{roles_db[r].category}]", roles_db[r].description)
                    for r in sorted_roles
                ]
                if command == "new":
                    chosen_role = ui.select("Select role:", role_options)
                    unparsed_roles = [chosen_role]
                else:
                    unparsed_roles = ui.multiselect(
                        f"Select roles for {command}:", role_options
                    )
                    if not unparsed_roles:
                        ui.warn("No roles selected. Exiting.")
                        sys.exit(0)
            else:
                ui.error(
                    f"Missing roles for command '{command}'. Example: flaker {command} python"
                )
                sys.exit(1)

        for item in unparsed_roles:
            raw_lower = item.lower()

            # 1. Check if alias directly maps to role:target
            if raw_lower in aliases and ":" in aliases[raw_lower]:
                r_part, _, t_part = aliases[raw_lower].partition(":")
                canonical_role = aliases.get(r_part.lower(), r_part.lower()).split(":", 1)[0]
                resolved_t = resolve_role_target(canonical_role, t_part, roles_db) or t_part
                if canonical_role in roles_db:
                    role_targets[canonical_role] = resolved_t
                    if canonical_role not in resolved_roles:
                        resolved_roles.append(canonical_role)
                    continue

            # 2. Colon notation (e.g. folio:slides, folio:paper, md:report, typst:report)
            if ":" in item:
                r_part, _, t_part = item.partition(":")
                canonical_role = aliases.get(r_part.lower(), r_part.lower()).split(":", 1)[0]
                if canonical_role in roles_db and roles_db[canonical_role].targets:
                    composite = f"{r_part.lower()}-{t_part.lower()}"
                    resolved_t = (
                        resolve_role_target(canonical_role, composite, roles_db)
                        or resolve_role_target(canonical_role, t_part, roles_db)
                    )
                    if not resolved_t:
                        valid_tgts = ", ".join(list(roles_db[canonical_role].targets.keys()))
                        ui.error(
                            f"Unknown target '{t_part}' for role '{canonical_role}'. Available targets: {valid_tgts}"
                        )
                        sys.exit(1)
                    role_targets[canonical_role] = resolved_t
                elif canonical_role not in roles_db:
                    ui.error(f"Unknown role '{r_part}'.")
                    sys.exit(1)
                if canonical_role not in resolved_roles:
                    resolved_roles.append(canonical_role)
                continue

            # 3. Check if item is a target for the immediately preceding role
            if resolved_roles:
                last_role = resolved_roles[-1]
                if last_role in roles_db and roles_db[last_role].targets and last_role not in role_targets:
                    resolved_t = resolve_role_target(last_role, item, roles_db)
                    if resolved_t:
                        role_targets[last_role] = resolved_t
                        continue
                    elif item.lower() not in roles_db and item.lower() not in aliases:
                        valid_tgts = ", ".join(list(roles_db[last_role].targets.keys()))
                        ui.error(
                            f"Unknown target '{item}' for role '{last_role}'. Available targets: {valid_tgts}"
                        )
                        sys.exit(1)

            # 4. Check if item is a standalone target for any role
            match = find_role_for_standalone_target(raw_lower, roles_db)
            if match and len(unparsed_roles) == 1:
                matched_role, matched_target = match
                if matched_role not in resolved_roles:
                    resolved_roles.append(matched_role)
                role_targets[matched_role] = matched_target
                continue

            # 5. Normal role name or alias
            aliased_val = aliases.get(raw_lower, raw_lower)
            canonical_role = aliased_val.split(":", 1)[0]
            if canonical_role not in resolved_roles:
                resolved_roles.append(canonical_role)

        if parsed.target_flag:
            for r in resolved_roles:
                if r in roles_db and roles_db[r].targets:
                    resolved_t = resolve_role_target(r, parsed.target_flag, roles_db)
                    if not resolved_t:
                        valid_tgts = ", ".join(list(roles_db[r].targets.keys()))
                        ui.error(
                            f"Unknown target '{parsed.target_flag}' for role '{r}'. Available targets: {valid_tgts}"
                        )
                        sys.exit(1)
                    role_targets[r] = resolved_t

        for r in resolved_roles:
            if r in roles_db and roles_db[r].targets and r not in role_targets:
                if command == "shell":
                    continue
                role_def = roles_db[r]
                if sys.stdin.isatty():
                    options = [
                        (
                            t_key,
                            f"{t_key.capitalize():<8} - {t_meta.get('description', '')}",
                            "",
                        )
                        for t_key, t_meta in role_def.targets.items()
                    ]
                    chosen = ui.select(f"Select template for {r}:", options)
                    role_targets[r] = chosen
                else:
                    role_targets[r] = (
                        "paper"
                        if "paper" in role_def.targets
                        else (
                            "report"
                            if "report" in role_def.targets
                            else list(role_def.targets.keys())[0]
                        )
                    )

    # Handle 'active' command (e.g. from interactive selector)
    if command == "active":
        display_active_roles(project_root, roles_db, aliases)
        sys.exit(0)

    # Handle 'packages' / 'pkg' command
    if command in ("packages", "pkg", "package"):
        preferred = unparsed_roles[0] if unparsed_roles else None
        configure_packages_interactive(preferred, dest_dir=current_dir)
        sys.exit(0)

    # Handle 'flaker new packages' / 'flaker new pkg'
    if command == "new" and unparsed_roles and unparsed_roles[0].lower() in ("packages", "pkg", "package"):
        preferred = unparsed_roles[1] if len(unparsed_roles) > 1 else None
        configure_packages_interactive(preferred, dest_dir=current_dir)
        sys.exit(0)

    # Enforce valid commands
    if command not in ("init", "new", "shell", "project"):
        ui.error(f"Unknown command '{command}'.\n")
        print_help()
        sys.exit(1)

    if not template_path.exists():
        ui.error(f"FLAKE_TEMPLATE path invalid or missing: {template_path}")
        sys.exit(1)

    nixpkgs_url = resolve_nixpkgs_url(parsed.channel)

    configure_packages = False
    if "folio" in resolved_roles:
        if parsed.no_packages_flag:
            configure_packages = False
        elif parsed.configure_packages_flag:
            configure_packages = True

    interactive_meta = (command == "new")

    doc_metadata = resolve_document_metadata(
        project_name=project_name,
        resolved_roles=resolved_roles,
        role_targets=role_targets,
        title_flag=parsed.doc_title,
        author_flag=parsed.doc_author,
        theme_flag=parsed.doc_theme,
        engine_flag=parsed.doc_engine,
        configure_packages=configure_packages,
        interactive=interactive_meta,
    )

    # 1. DevShell generation (init and shell)
    if command in ("init", "shell"):
        init_root = current_dir if command == "init" else project_root
        success = prepare_flake_env(
            project_root=init_root,
            resolved_roles=resolved_roles,
            roles_db=roles_db,
            template_path=template_path,
            libs_list=libs_list,
            nixpkgs_url=nixpkgs_url,
            force=parsed.force,
            dry_run=parsed.dry_run,
            auto_git=parsed.auto_git,
            no_direnv=parsed.no_direnv,
        )
        if not success:
            sys.exit(0)

    # 2. Project foundation scaffolding
    if command == "init":
        scaffold_assets(
            target_dir=current_dir,
            project_name=project_name,
            resolved_roles=resolved_roles,
            assets_dirs=all_asset_dirs,
            scope="project",
            force=parsed.force,
            dry_run=parsed.dry_run,
            auto_git=parsed.auto_git,
            project_root=current_dir,
            role_targets=role_targets,
            roles_db=roles_db,
            metadata=doc_metadata,
        )
        scaffold_assets(
            target_dir=current_dir,
            project_name=project_name,
            resolved_roles=resolved_roles,
            assets_dirs=all_asset_dirs,
            scope="starter",
            force=parsed.force,
            dry_run=parsed.dry_run,
            auto_git=parsed.auto_git,
            project_root=current_dir,
            role_targets=role_targets,
            roles_db=roles_db,
        )

    elif command == "project":
        scaffold_assets(
            target_dir=project_root,
            project_name=project_name,
            resolved_roles=resolved_roles,
            assets_dirs=all_asset_dirs,
            scope="project",
            force=parsed.force,
            dry_run=parsed.dry_run,
            auto_git=parsed.auto_git,
            project_root=project_root,
            role_targets=role_targets,
            roles_db=roles_db,
            metadata=doc_metadata,
        )

    elif command == "new":
        scaffold_assets(
            target_dir=current_dir,
            project_name=project_name,
            resolved_roles=resolved_roles,
            assets_dirs=all_asset_dirs,
            scope="starter",
            force=parsed.force,
            dry_run=parsed.dry_run,
            auto_git=parsed.auto_git,
            project_root=project_root,
            role_targets=role_targets,
            roles_db=roles_db,
            metadata=doc_metadata,
        )
