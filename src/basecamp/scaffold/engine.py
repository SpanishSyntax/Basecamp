"""Asset scaffolding and template rendering engine for Basecamp."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any

from basecamp.core.models import Role
from basecamp.scaffold.git import get_git_author, stage_git_files
from basecamp.ui import ui


def resolve_metadata(
    project_name: str,
    author_flag: str | None = None,
    **kwargs: Any,
) -> dict[str, str]:
    """Resolves basic project metadata for template rendering."""
    git_author = get_git_author()
    return {
        "project_name": project_name,
        "author": author_flag or (git_author if git_author else "Author"),
        "date": time.strftime("%B %Y"),
    }


# Backwards compatibility alias
resolve_document_metadata = resolve_metadata


def scaffold_assets(
    target_dir: Path,
    project_name: str,
    resolved_roles: list[str],
    assets_dirs: list[Path],
    scope: str = "starter",
    force: bool = False,
    dry_run: bool = False,
    auto_git: bool = True,
    project_root: Path | None = None,
    role_targets: dict[str, str] | None = None,
    roles_db: dict[str, Role] | None = None,
    metadata: dict[str, str] | None = None,
) -> bool:
    """Copies role templates into the target directory based on scope:

    - 'project': Copies files from role/project/ into target_dir (usually project_root)
    - 'starter': Copies files from role/starter/ into target_dir (usually current_dir)
    - 'all': Copies both project and starter assets
    """
    scaffolded_any = False
    created_files: list[str] = []

    for role_key in resolved_roles:
        found_in_dir = False

        for adir in assets_dirs:
            role_assets_dir = adir / role_key
            if not role_assets_dir.exists():
                continue

            found_in_dir = True
            has_project_subdir = (role_assets_dir / "project").is_dir()
            has_starter_subdir = (role_assets_dir / "starter").is_dir()

            subdirs_to_copy: list[Path] = []
            if has_project_subdir or has_starter_subdir:
                if scope in ("project", "all") and has_project_subdir:
                    subdirs_to_copy.append(role_assets_dir / "project")
                if scope in ("starter", "all") and has_starter_subdir:
                    subdirs_to_copy.append(role_assets_dir / "starter")
            else:
                subdirs_to_copy.append(role_assets_dir)

            for src_dir in subdirs_to_copy:
                for template_file in src_dir.glob("**/*"):
                    if not template_file.is_file():
                        continue
                    if "__pycache__" in template_file.parts or template_file.suffix in (
                        ".pyc",
                        ".pyo",
                    ):
                        continue

                    relative_path = template_file.relative_to(src_dir)
                    dest_path = target_dir / relative_path

                    if dry_run:
                        ui.info(
                            f"[DRY RUN] Would scaffold {relative_path} into {dest_path}"
                        )
                        scaffolded_any = True
                        continue

                    if dest_path.exists() and not force:
                        if sys.stdin.isatty():
                            prompt_msg = f"{ui.badge()} {ui.yellow(f'⚠️  {dest_path.name} already exists. Overwrite? [y/N]: ')}"
                            try:
                                ans = input(prompt_msg).strip().lower()
                                if ans not in ("y", "yes"):
                                    ui.warn(
                                        f"Skipped {dest_path.name} (preserved existing file)"
                                    )
                                    continue
                            except (KeyboardInterrupt, EOFError):
                                print("\nAborted.")
                                return scaffolded_any
                        else:
                            ui.warn(
                                f"Skipped {dest_path.name} (file already exists; use -f/--force to overwrite)"
                            )
                            continue

                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    content = template_file.read_text(encoding="utf-8")
                    content = content.replace("__PROJECT_NAME__", project_name)
                    if metadata:
                        for mk, mv in metadata.items():
                            if isinstance(mv, str):
                                content = content.replace(f"__{mk.upper()}__", mv)

                    dest_path.write_text(content, encoding="utf-8")
                    scaffolded_any = True
                    created_files.append(str(dest_path.relative_to(target_dir)))

            if found_in_dir:
                break

    if scaffolded_any and not dry_run:
        scope_desc = (
            "project foundation"
            if scope == "project"
            else ("starter" if scope == "starter" else "")
        )
        ui.success(f"Scaffolded {scope_desc} assets into {target_dir}")
        if auto_git:
            stage_git_files(project_root or target_dir, created_files)

    return scaffolded_any
