"""Git integration and .gitignore generation for Basecamp."""

import os
import subprocess
from pathlib import Path

from basecamp.core.models import Role
from basecamp.ui import ui


def get_git_author() -> str:
    """Retrieves git user.name if configured."""
    try:
        res = subprocess.run(
            ["git", "config", "user.name"], capture_output=True, text=True
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return ""


def stage_git_files(project_root: Path, files: list[str]) -> None:
    """Automatically runs 'git add' on created files if inside a git repository."""
    if not (project_root / ".git").exists():
        return
    try:
        valid_files = [f for f in files if (project_root / f).exists()]
        if valid_files:
            subprocess.run(
                ["git", "add"] + valid_files,
                cwd=project_root,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            ui.action(f"Auto-staged {', '.join(valid_files)} with git add", symbol="📦")
    except Exception:
        pass


def update_gitignore(
    project_root: Path,
    resolved_roles: list[str],
    roles_db: dict[str, Role],
    dry_run: bool = False,
) -> bool:
    """Creates or updates .gitignore with standard Nix/direnv, Frost SSOT, and role-specific ignores."""
    gitignore_path = project_root / ".gitignore"
    existing_content = ""
    if gitignore_path.exists():
        existing_content = gitignore_path.read_text(encoding="utf-8")

    existing_lines = {
        line.strip()
        for line in existing_content.splitlines()
        if line.strip() and not line.strip().startswith("#")
    }

    new_sections: list[str] = []

    # 1. Frost Global Environment Ignores (The SSOT Hook)
    frost_ignore_path = Path.home() / ".config/frost/global_ignores"
    if frost_ignore_path and os.path.exists(frost_ignore_path):
        try:
            frost_content = Path(frost_ignore_path).read_text(encoding="utf-8")
            frost_rules = [
                line.strip()
                for line in frost_content.splitlines()
                if line.strip() and not line.startswith("#")
            ]
            missing_frost = [r for r in frost_rules if r not in existing_lines]
            if missing_frost:
                new_sections.append(
                    "# Frost Global Environment\n" + "\n".join(missing_frost)
                )
                existing_lines.update(missing_frost)
        except Exception:
            pass

    # 2. Base Nix & Direnv rules
    base_rules = [".direnv/", "result", "result-*"]
    missing_base = [r for r in base_rules if r not in existing_lines]
    if missing_base:
        new_sections.append("# Nix & Direnv\n" + "\n".join(missing_base))
        existing_lines.update(missing_base)

    # 3. Role-specific rules
    for r in resolved_roles:
        if r in roles_db and roles_db[r].ignores:
            missing = [ign for ign in roles_db[r].ignores if ign not in existing_lines]
            if missing:
                new_sections.append(
                    f"# {roles_db[r].category} ({r})\n" + "\n".join(missing)
                )
                existing_lines.update(missing)

    if not new_sections:
        return False

    append_text = "\n\n" + "\n\n".join(new_sections) + "\n"
    if dry_run:
        ui.subheader("[DRY RUN] .gitignore additions", width=76)
        print(append_text.strip())
        return True

    final_content = (existing_content.rstrip() + append_text).lstrip()
    gitignore_path.write_text(final_content, encoding="utf-8")
    ui.success(f"Updated .gitignore at {project_root}")
    return True
