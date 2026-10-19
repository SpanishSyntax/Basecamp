"""Flake environment preparation and project detection for Flaker."""

import shutil
import subprocess
import sys
from pathlib import Path

from flaker.core.models import Role
from flaker.scaffold.git import stage_git_files, update_gitignore
from flaker.ui import ui


def get_project_name(root_path: Path) -> str:
    """Derives a normalized project name from root directory name."""
    return root_path.name.replace(" ", "_")


def find_project_root(current_dir: Path) -> Path:
    """
    Traverse upwards to find the project root.
    Looks for an existing flake.nix or .git folder.
    Falls back to the current directory if nothing is found.
    """
    for p in [current_dir, *current_dir.parents]:
        if (p / "flake.nix").exists() or (p / ".git").exists():
            return p
    return current_dir


def prepare_flake_env(
    project_root: Path,
    resolved_roles: list[str],
    roles_db: dict[str, Role],
    template_path: Path,
    libs_list: str,
    nixpkgs_url: str,
    force: bool = False,
    dry_run: bool = False,
    auto_git: bool = True,
    no_direnv: bool = False,
) -> bool:
    """Generates the flake.nix and .envrc at the project root."""
    flake_out = project_root / "flake.nix"
    envrc_out = project_root / ".envrc"

    if not force and not dry_run and flake_out.exists():
        if sys.stdin.isatty():
            try:
                prompt_msg = f"{ui.badge()} {ui.yellow(f'⚠️  flake.nix already exists at {project_root}. Overwrite? [y/N]: ')}"
                ans = input(prompt_msg).strip().lower()
                if ans not in ("y", "yes"):
                    ui.warn("Aborted: existing flake.nix was preserved.")
                    return False
            except (KeyboardInterrupt, EOFError):
                print("\nAborted.")
                return False
        else:
            ui.error(f"{flake_out} already exists. Pass --force to overwrite.")
            sys.exit(1)

    selected_pkgs: list[str] = []
    selected_hooks: list[str] = []

    for role_key in resolved_roles:
        if role_key in roles_db:
            role = roles_db[role_key]
            selected_pkgs.extend(role.pkgs)
            selected_hooks.extend(role.hooks)
        else:
            selected_pkgs.append(role_key)

    has_rust = "rust" in resolved_roles

    rust_input = (
        '    rust-overlay.url = "github:oxalica/rust-overlay";\n'
        '    rust-overlay.inputs.nixpkgs.follows = "nixpkgs";'
        if has_rust
        else ""
    )
    rust_overlay = (
        "overlays = [ inputs.rust-overlay.overlays.default ];" if has_rust else ""
    )

    template_content = template_path.read_text(encoding="utf-8")

    rendered = (
        template_content.replace("__NIXPKGS_URL__", nixpkgs_url)
        .replace("/* __RUST_INPUT__ */", rust_input)
        .replace("/* __RUST_OVERLAY__ */", rust_overlay)
        .replace("__LIBS_LIST__", libs_list)
        .replace("__PKGS_LIST__", " ".join(selected_pkgs))
        .replace("__SHELL_HOOKS__", "\n          ".join(selected_hooks))
    )

    if dry_run:
        ui.subheader(
            f"[DRY RUN] Generated flake.nix (Channel: {nixpkgs_url})", width=76
        )
        print(rendered)
        if not no_direnv:
            ui.subheader("[DRY RUN] Generated .envrc", width=76)
            print("use flake\n")
        update_gitignore(project_root, resolved_roles, roles_db, dry_run=True)
        return True

    flake_out.write_text(rendered, encoding="utf-8")

    if not no_direnv:
        if not envrc_out.exists():
            envrc_out.write_text("use flake\n", encoding="utf-8")
        if shutil.which("direnv"):
            try:
                subprocess.run(["direnv", "allow"], cwd=project_root, check=False)
            except Exception:
                pass

    update_gitignore(project_root, resolved_roles, roles_db, dry_run=False)

    msg = (
        f"Generated flake.nix at {project_root}"
        if no_direnv
        else f"Generated flake.nix and .envrc at {project_root}"
    )
    ui.success(msg)

    if auto_git:
        stage_files = ["flake.nix", ".gitignore"]
        if not no_direnv:
            stage_files.append(".envrc")
        stage_git_files(project_root, stage_files)

    return True
