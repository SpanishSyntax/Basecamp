"""Asset scaffolding and template rendering engine for Flaker."""

import sys
import time
from pathlib import Path

from flaker.core.models import Role
from flaker.scaffold.git import get_git_author, stage_git_files
from flaker.scaffold.manifests import (
    LATEX_PACKAGE_BUNDLES,
    TYPST_PACKAGE_BUNDLES,
    generate_packages_manifest,
)
from flaker.ui import ui


def resolve_document_metadata(
    project_name: str,
    resolved_roles: list[str],
    role_targets: dict[str, str],
    title_flag: str | None = None,
    author_flag: str | None = None,
    theme_flag: str | None = None,
    engine_flag: str | None = None,
    configure_packages: bool = False,
    interactive: bool = True,
) -> dict[str, str]:
    """Interactively prompts or resolves document metadata when scaffolding Folio documents."""
    meta: dict[str, str] = {}
    if "folio" not in resolved_roles:
        return meta

    meta["date"] = time.strftime("%B %Y")
    meta["dependency"] = "Department of Systems & Control"

    target = role_targets.get("folio", "")
    git_author = get_git_author()
    default_title = project_name.replace("-", " ").replace("_", " ").title()
    default_author = git_author if git_author else "Author"

    is_markdown_target = target in ("report", "slides", "paper", "")

    if interactive and sys.stdin.isatty():
        # Title
        if title_flag:
            meta["title"] = title_flag
        else:
            meta["title"] = ui.prompt("Document title", default=default_title)

        # Author
        if author_flag:
            meta["author"] = author_flag
        else:
            meta["author"] = ui.prompt("Author", default=default_author)

        # Engine (prompted specifically for Markdown workspaces)
        if is_markdown_target:
            if engine_flag:
                meta["engine"] = engine_flag.lower()
            else:
                meta["engine"] = ui.select(
                    "Select compilation engine for Markdown:",
                    [
                        ("typst", "Typst (recommended, ultra-fast hermetic layout)"),
                        ("latex", "LaTeX (Tectonic + Pandoc, academic TeX typesetting)"),
                    ],
                )
        elif target.startswith("latex") or target.startswith("tex"):
            meta["engine"] = "latex"
        else:
            meta["engine"] = "typst"

        # Theme (specifically for presentation slides)
        if target in ("slides", "") or "slides" in target:
            if theme_flag:
                meta["theme"] = theme_flag.lower()
            else:
                meta["theme"] = ui.select(
                    "Select presentation theme:",
                    [
                        ("dark", "Dark theme (recommended, 16:9 OLED Keynote style)"),
                        ("light", "Light theme (clean paper / lecture style)"),
                    ],
                )
        elif theme_flag:
            meta["theme"] = theme_flag.lower()
        else:
            meta["theme"] = "dark"

        if configure_packages:
            is_tex = (
                (meta.get("engine") == "latex")
                or target.startswith("latex")
                or target.startswith("tex")
            )
            fmt = "latex" if is_tex else "typst"
            bundles = LATEX_PACKAGE_BUNDLES if is_tex else TYPST_PACKAGE_BUNDLES
            options = [(b["id"], b["label"], b["desc"]) for b in bundles]
            preselected = [b["id"] for b in bundles if b.get("default", False)]
            chosen_ids = ui.multiselect(
                f"Select {fmt.title()} packages to include:",
                options,
                preselected=preselected,
            )
            key = f"packages_{'tex' if is_tex else 'typ'}_content"
            meta[key] = generate_packages_manifest(
                fmt, chosen_ids if chosen_ids else preselected
            )
    else:
        meta["title"] = title_flag or default_title
        meta["author"] = author_flag or default_author
        meta["theme"] = theme_flag.lower() if theme_flag else "dark"
        if is_markdown_target:
            meta["engine"] = engine_flag.lower() if engine_flag else "typst"
        elif target.startswith("latex") or target.startswith("tex"):
            meta["engine"] = "latex"
        else:
            meta["engine"] = "typst"

    return meta


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
    """
    Copies role templates into the target directory based on scope:
      - 'project': Copies files from role/project/ into target_dir (usually project_root)
      - 'starter': Copies files from role/starter/ into target_dir (usually current_dir)
      - 'all': Copies both project and starter assets
    Filters files based on role_targets if specified.
    """
    scaffolded_any = False
    created_files: list[str] = []
    targets_map = role_targets or {}

    for role_key in resolved_roles:
        found_in_dir = False
        target_name = targets_map.get(role_key)
        role_def = roles_db.get(role_key) if roles_db else None

        for adir in assets_dirs:
            role_assets_dir = adir / role_key
            if not role_assets_dir.exists():
                continue

            found_in_dir = True
            has_project_subdir = (role_assets_dir / "project").is_dir()
            has_starter_subdir = (role_assets_dir / "starter").is_dir()

            subdirs_to_copy: list[tuple[Path, str]] = []
            if has_project_subdir or has_starter_subdir:
                if scope in ("project", "all") and has_project_subdir:
                    subdirs_to_copy.append((role_assets_dir / "project", "project"))
                if scope in ("starter", "all") and has_starter_subdir:
                    subdirs_to_copy.append((role_assets_dir / "starter", "starter"))
            else:
                # Flat legacy directory
                subdirs_to_copy.append((role_assets_dir, "flat"))

            for src_dir, dir_type in subdirs_to_copy:
                allowed_files: list[str] | None = None
                if (
                    role_def
                    and role_def.targets
                    and target_name
                    and target_name != "all"
                    and target_name in role_def.targets
                ):
                    target_spec = role_def.targets[target_name]
                    if dir_type in ("project", "starter"):
                        allowed_files = list(target_spec.get(dir_type, []))
                    else:
                        allowed_files = list(target_spec.get("project", [])) + list(
                            target_spec.get("starter", [])
                        )

                    # Dynamic engine filtering for Markdown targets
                    if target_name in ("report", "slides", "paper") and dir_type == "project":
                        if metadata and metadata.get("engine") == "latex":
                            allowed_files = ["packages.tex", "library.bib"]
                        else:
                            allowed_files = [
                                "packages.typ",
                                f"{target_name}.typ",
                                "library.bib",
                            ]

                files_to_process: list[tuple[Path, Path]] = []
                if allowed_files is not None:
                    for rel_str in allowed_files:
                        rel_p = Path(rel_str)
                        primary = src_dir / rel_p
                        fallback = (
                            (role_assets_dir / "starter" / rel_p)
                            if dir_type == "project"
                            else None
                        )
                        if primary.is_file():
                            files_to_process.append((primary, rel_p))
                        elif fallback and fallback.is_file():
                            files_to_process.append((fallback, rel_p))
                else:
                    for template_file in src_dir.glob("**/*"):
                        if template_file.is_file():
                            if (
                                "__pycache__" in template_file.parts
                                or template_file.suffix in (".pyc", ".pyo")
                            ):
                                continue
                            relative_path = template_file.relative_to(src_dir)
                            files_to_process.append((template_file, relative_path))

                for template_file, relative_path in files_to_process:
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
                    if (
                        dest_path.name == "packages.typ"
                        and metadata
                        and metadata.get("packages_typ_content")
                    ):
                        content = metadata["packages_typ_content"]
                    elif (
                        dest_path.name == "packages.tex"
                        and metadata
                        and metadata.get("packages_tex_content")
                    ):
                        content = metadata["packages_tex_content"]
                    else:
                        content = template_file.read_text(encoding="utf-8")
                    content = content.replace("__PROJECT_NAME__", project_name)
                    if metadata:
                        for mk, mv in metadata.items():
                            val = mv
                            if (
                                dest_path.suffix == ".tex"
                                and isinstance(val, str)
                                and not mk.startswith("packages_")
                            ):
                                val = val.replace("&", r"\&")
                            content = content.replace(f"__{mk.upper()}__", val)
                    # Fallback defaults for unreplaced placeholders
                    title_fb = project_name.replace("-", " ").replace("_", " ").title()
                    subtitle_fb = (
                        "16:9 Technical Systems Presentation"
                        if "slides" in dest_path.name
                        else "Technical Systems Engineering Report"
                    )
                    author_fb = get_git_author() or "Author"
                    dep_fb = "Department of Systems & Control"
                    system_date = time.strftime("%B %Y")
                    date_fb = (metadata.get("date") if metadata else None) or system_date

                    if dest_path.suffix == ".tex":
                        title_fb = title_fb.replace("&", r"\&")
                        subtitle_fb = subtitle_fb.replace("&", r"\&")
                        author_fb = author_fb.replace("&", r"\&")
                        dep_fb = dep_fb.replace("&", r"\&")
                        date_fb = date_fb.replace("&", r"\&")

                    content = content.replace("__TITLE__", title_fb)
                    content = content.replace("__SUBTITLE__", subtitle_fb)
                    content = content.replace("__AUTHOR__", author_fb)
                    content = content.replace("__DEPENDENCY__", dep_fb)
                    content = content.replace("__THEME__", "dark")
                    content = content.replace(
                        "__ENGINE__",
                        metadata.get("engine", "typst") if metadata else "typst",
                    )
                    content = content.replace("__DATE__", date_fb)
                    dest_path.write_text(content, encoding="utf-8")
                    scaffolded_any = True
                    created_files.append(str(dest_path.relative_to(target_dir)))

            if found_in_dir:
                break

    if scaffolded_any and not dry_run:
        target_labels = [
            f"{r}:{targets_map[r]}" for r in resolved_roles if targets_map.get(r)
        ]
        target_info = f" ({', '.join(target_labels)})" if target_labels else ""
        scope_desc = (
            "project foundation"
            if scope == "project"
            else ("starter" if scope == "starter" else "")
        )
        ui.success(f"Scaffolded {scope_desc}{target_info} assets into {target_dir}")
        if auto_git:
            stage_git_files(project_root or target_dir, created_files)

    return scaffolded_any
