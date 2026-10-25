"""Handler for 'basecamp info <role>' command."""

import sys
from pathlib import Path

from basecamp.core.models import Role
from basecamp.ui import ui


def display_role_info(
    role_name: str,
    roles_db: dict[str, Role],
    aliases: dict[str, str],
    assets_dirs: list[Path],
) -> None:
    """Displays detailed configuration and packages for a given role."""
    clean_input = role_name.strip().lower()
    aliased_target = aliases.get(clean_input, clean_input)
    resolved_name = aliased_target.split(":", 1)[0]
    if resolved_name not in roles_db:
        ui.error(
            f"Unknown role '{role_name}'. Run 'basecamp list' to see available roles."
        )
        sys.exit(1)

    role = roles_db[resolved_name]
    rev_aliases = [a for a, t in aliases.items() if t == resolved_name]

    ui.header(f"Role Information: {resolved_name}", width=76)
    print(f"  {ui.bold('Category')}    : {role.category}")
    print(
        f"  {ui.bold('Aliases')}     : {', '.join(sorted(rev_aliases)) if rev_aliases else ui.dim('none')}"
    )
    print(f"  {ui.bold('Summary')}     : {role.description}")

    if role.targets:
        print(
            f"\n  {ui.bold('Available Document Targets (--target, -m, or positional):')}"
        )
        for t_name, t_meta in role.targets.items():
            aliases_str = (
                f" [aliases: {', '.join(t_meta.get('aliases', []))}]"
                if t_meta.get("aliases")
                else ""
            )
            desc = t_meta.get("description", "")
            print(f"    • {ui.cyan(t_name):<10} : {desc}{ui.dim(aliases_str)}")

    print(f"\n  {ui.bold('Packages Included in DevShell:')}")
    for pkg in role.pkgs:
        print(f"    • {ui.cyan(pkg)}")

    print(f"\n  {ui.bold('Shell Activation Hooks:')}")
    for hook in role.hooks:
        print(f"    • {ui.dim(hook)}")

    if role.targets:
        print(f"\n  {ui.bold('Template Assets by Target:')}")
        for t_name, t_meta in role.targets.items():
            p_files = t_meta.get("project", [])
            s_files = t_meta.get("starter", [])
            details = []
            if p_files:
                details.append(f"foundation: {', '.join(p_files)}")
            if s_files:
                details.append(f"starter: {', '.join(s_files)}")
            print(f"    📦 {ui.cyan(t_name):<10} -> {'; '.join(details)}")

    # Inspect template files
    project_files: list[str] = []
    starter_files: list[str] = []
    for adir in assets_dirs:
        rdir = adir / resolved_name
        if rdir.exists():
            pdir = rdir / "project"
            sdir = rdir / "starter"
            if pdir.exists() or sdir.exists():
                if pdir.exists():
                    for f in pdir.glob("**/*"):
                        if (
                            f.is_file()
                            and "__pycache__" not in f.parts
                            and f.suffix not in (".pyc", ".pyo")
                        ):
                            project_files.append(str(f.relative_to(pdir)))
                if sdir.exists():
                    for f in sdir.glob("**/*"):
                        if (
                            f.is_file()
                            and "__pycache__" not in f.parts
                            and f.suffix not in (".pyc", ".pyo")
                        ):
                            starter_files.append(str(f.relative_to(sdir)))
            else:
                for f in rdir.glob("**/*"):
                    if (
                        f.is_file()
                        and "__pycache__" not in f.parts
                        and f.suffix not in (".pyc", ".pyo")
                    ):
                        starter_files.append(str(f.relative_to(rdir)))
            break

    if not role.targets:
        if project_files:
            print(f"\n  {ui.bold('Project Root Foundation Files (basecamp project):')}")
            for pf in project_files:
                print(f"    📦 {ui.cyan(pf)}")

        if starter_files:
            print(f"\n  {ui.bold('Starter / Leaf Files (basecamp new):')}")
            for sf in starter_files:
                print(f"    📄 {ui.green(sf)}")
        elif not project_files:
            print(f"\n  {ui.bold('Template Files:')}")
            print(f"    {ui.dim('(No template files for this role; DevShell only)')}")

    if role.ignores:
        print(f"\n  {ui.bold('Default .gitignore Rules:')}")
        for ign in role.ignores:
            print(f"    🚫 {ui.dim(ign)}")

    print(ui.blue("=" * 76) + "\n")
