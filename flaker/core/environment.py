"""Flake environment preparation and project detection for Flaker."""

import re
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


def build_shell_hooks(
    resolved_roles: list[str],
    roles_db: dict[str, Role],
) -> list[str]:
    """Constructs the unified Option C shell hook with error trapping and status badges."""
    lines: list[str] = ["_flk_err=0"]

    # 1. Per-role error flags and setup commands
    for r_key in resolved_roles:
        safe_key = re.sub(r"[^a-zA-Z0-9_]", "_", r_key)
        lines.append(f"_flk_err_{safe_key}=0")
        if r_key in roles_db:
            role = roles_db[r_key]
            for hook in role.hooks:
                # Exclude any legacy fmt_status printf lines
                if "❄️  [flaker]" in hook and "\\033[1m" in hook:
                    continue
                lines.append(hook)

    # 2. Consolidated status badge block
    lines.append(
        "printf '\\033[1;34m❄️  [flaker]\\033[0m \\033[1mWorkspace Initialized:\\033[0m\\n'"
    )
    for r_key in resolved_roles:
        safe_key = re.sub(r"[^a-zA-Z0-9_]", "_", r_key)
        if r_key in roles_db:
            role = roles_db[r_key]
            icon = getattr(role, "icon", None) or "❄️"
            name = getattr(role, "display_name", None) or r_key.title()
            detail = getattr(role, "status_detail", None) or role.description
        else:
            icon = "📦"
            name = r_key
            detail = "Package"

        extra_ok = f" \\033[2m({detail})\\033[0m" if detail else ""
        lines.append(
            f'if [ "$_flk_err_{safe_key}" -eq 0 ]; then\n'
            f"            printf ' \\033[2m│\\033[0m  \\033[1;32m✓\\033[0m {icon} \\033[1m{name}\\033[0m{extra_ok}\\n'\n"
            f"          else\n"
            f"            printf ' \\033[2m│\\033[0m  \\033[1;31m✗\\033[0m {icon} \\033[1m{name}\\033[0m \\033[1;31m(setup failed)\\033[0m\\n'\n"
            f"          fi"
        )

    # 3. Notification on failure
    lines.append(
        'if [ "$_flk_err" -ne 0 ]; then\n'
        '            type notify-send >/dev/null 2>&1 && notify-send -u critical "❄️ Flaker" "Workspace role setup failed in $(basename "$PWD")"\n'
        '          fi'
    )

    return lines


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

    for role_key in resolved_roles:
        if role_key in roles_db:
            role = roles_db[role_key]
            selected_pkgs.extend(role.pkgs)
        else:
            selected_pkgs.append(role_key)

    selected_hooks = build_shell_hooks(resolved_roles, roles_db)

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
        template_content.replace("__ROLES_LIST__", " ".join(resolved_roles))
        .replace("__NIXPKGS_URL__", nixpkgs_url)
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
