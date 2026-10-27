"""Handler for 'basecamp active' and 'basecamp list --active' commands."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from basecamp.core.models import Role
from basecamp.ui import ui

BANNER_NAME_TO_ROLE: dict[str, str] = {
    "rust": "rust",
    "c": "c",
    "c++": "cpp",
    "go": "go",
    "zig": "zig",
    "java": "java",
    ".net": "dotnet",
    "python": "python",
    "barograph": "barograph",
    "julia": "julia",
    "js/ts": "ts",
    "svelte 5": "svelte",
    "vue": "vue",
    "next.js": "next",
    "gleam": "gleam",
    "elixir": "elixir",
    "haskell": "haskell",
    "snowpack": "snowpack",
    "devops": "ops",
}

KNOWN_PROJECT_ARTIFACTS: list[tuple[str, str]] = [
    ("pyproject.toml", "Python"),
    ("requirements.txt", "Python"),
    ("main.py", "Python"),
    ("uv.lock", "Python"),
    ("Cargo.toml", "Rust"),
    ("src/main.rs", "Rust"),
    ("src/lib.rs", "Rust"),
    ("report.typ", "Snowpack/Typst"),
    ("slides.typ", "Snowpack/Typst"),
    ("paper.typ", "Snowpack/Typst"),
    ("packages.typ", "Snowpack/Typst"),
    ("report.tex", "Snowpack/LaTeX"),
    ("slides.tex", "Snowpack/LaTeX"),
    ("paper.tex", "Snowpack/LaTeX"),
    ("packages.tex", "Snowpack/LaTeX"),
    ("report.md", "Snowpack/Markdown"),
    ("slides.md", "Snowpack/Markdown"),
    ("paper.md", "Snowpack/Markdown"),
    ("go.mod", "Go"),
    ("main.go", "Go"),
    ("package.json", "Node/Bun/TS"),
    ("index.ts", "TypeScript"),
    ("CMakeLists.txt", "C/C++"),
    ("main.c", "C"),
    ("main.cpp", "C++"),
    ("build.zig", "Zig"),
    ("pom.xml", "Java"),
    ("build.gradle", "Java"),
    ("mix.exs", "Elixir"),
    ("gleam.toml", "Gleam"),
    ("compose.yaml", "DevOps"),
    ("docker-compose.yml", "DevOps"),
    ("Dockerfile", "DevOps"),
]


@dataclass
class ActiveRoleDiagnostic:
    """Diagnostic details of an active role in a flake."""

    role_key: str
    role: Role
    detection_method: str  # 'metadata', 'hook', or 'packages'


@dataclass
class FlakeWorkspaceDiagnosis:
    """Complete diagnostic representation of the active flake workspace."""

    project_root: Path
    flake_path: Path
    channel: str | None = None
    active_roles: list[ActiveRoleDiagnostic] = field(default_factory=list)
    extra_packages: list[str] = field(default_factory=list)
    discovered_artifacts: list[str] = field(default_factory=list)


def detect_active_roles(
    flake_content: str,
    roles_db: dict[str, Role],
    aliases: dict[str, str],
) -> tuple[list[ActiveRoleDiagnostic], list[str], str | None]:
    """
    Parses flake.nix content to detect active roles, extra packages, and nixpkgs channel.
    Uses a multi-tier resolution strategy:
      1. Explicit Basecamp metadata tag comment: `# [basecamp] roles: <roles>`
      2. Shell hook banner matching: `printf '...⛺  [basecamp]... <name> ...active'`
      3. Package signature matching from `packages = with pkgs; [...]`
    """
    detected: dict[str, ActiveRoleDiagnostic] = {}

    # Extract channel / nixpkgs URL
    channel: str | None = None
    chan_match = re.search(r'nixpkgs\.url\s*=\s*"([^"]+)";', flake_content)
    if chan_match:
        url = chan_match.group(1)
        # Extract short channel name if it's standard nixpkgs
        if "nixos-" in url or "nixpkgs-" in url:
            channel = url.split("/")[-1]
        else:
            channel = url

    # 1. Check explicit Basecamp roles metadata comment
    comment_match = re.search(
        r"#\s*\[basecamp\]\s*roles:\s*(.+)$", flake_content, re.MULTILINE | re.IGNORECASE
    )
    if comment_match:
        raw_tokens = comment_match.group(1).split()
        for tok in raw_tokens:
            tok_clean = tok.strip().lower()
            aliased = aliases.get(tok_clean, tok_clean).split(":", 1)[0]
            if aliased in roles_db and aliased not in detected:
                detected[aliased] = ActiveRoleDiagnostic(
                    role_key=aliased,
                    role=roles_db[aliased],
                    detection_method="metadata",
                )

    # 2. Check shell hooks for status banners and hook matches
    banner_matches = re.findall(
        r"\[basecamp\]\\033\[0m.*?\\033\[1m([^\\]+)\\033\[0m.*?active", flake_content
    )
    badge_matches = re.findall(
        r"\\033\[1m([^\\]+)\\033\[0m\s*\\033\[2m", flake_content
    )
    for b_name in banner_matches + badge_matches:
        clean_b = b_name.strip().lower()
        role_key = BANNER_NAME_TO_ROLE.get(clean_b, clean_b)
        aliased = aliases.get(role_key, role_key).split(":", 1)[0]
        if aliased in roles_db and aliased not in detected:
            detected[aliased] = ActiveRoleDiagnostic(
                role_key=aliased,
                role=roles_db[aliased],
                detection_method="hook",
            )

    # Fallback hook matching: check if role hook snippets appear directly in flake
    for r_key, role in roles_db.items():
        if r_key not in detected:
            for hook in role.hooks:
                # If a significant part of the hook is present
                if hook and (hook in flake_content or hook.splitlines()[0] in flake_content):
                    detected[r_key] = ActiveRoleDiagnostic(
                        role_key=r_key,
                        role=role,
                        detection_method="hook",
                    )
                    break

    # 3. Extract packages list
    pkg_match = re.search(
        r"packages\s*=\s*with\s+pkgs;\s*\[(.*?)\];", flake_content, re.DOTALL
    )
    flake_pkgs: set[str] = set()
    if pkg_match:
        # Split tokens, strip parentheses, strings, etc.
        raw_pkgs = pkg_match.group(1)
        tokens = re.findall(r"[A-Za-z0-9_.-]+", raw_pkgs)
        flake_pkgs = {
            t
            for t in tokens
            if t not in ("with", "pkgs", "override", "extensions", "rust-bin")
        }

    # Distinctive package signatures for fallback matching
    SIGNATURE_PKGS: dict[str, list[str]] = {
        "python": ["uv", "python314", "python313", "python312", "python3"],
        "rust": ["cargo-expand", "lldb"],
        "c": ["clang-tools", "ninja"],
        "cpp": ["boost", "eigen"],
        "go": ["gopls", "golangci-lint"],
        "zig": ["zls"],
        "java": ["jdt-language-server"],
        "dotnet": ["dotnet-sdk", "omnisharp-roslyn"],
        "barograph": ["barograph", "scipy", "matplotlib"],
        "julia": ["julia-bin"],
        "ts": ["prettierd", "vtsls"],
        "svelte": ["svelte-language-server"],
        "vue": ["vue-language-server"],
        "gleam": ["gleam"],
        "elixir": ["elixir-ls"],
        "haskell": ["haskell-language-server", "cabal-install"],
        "snowpack": ["typstyle", "typst"],
        "ops": ["kubectl", "k9s"],
    }

    for r_key, sigs in SIGNATURE_PKGS.items():
        if r_key not in detected and r_key in roles_db:
            if any(sig in flake_pkgs or sig in flake_content for sig in sigs):
                detected[r_key] = ActiveRoleDiagnostic(
                    role_key=r_key,
                    role=roles_db[r_key],
                    detection_method="packages",
                )

    # 4. Compute extra standalone packages
    known_role_pkgs: set[str] = set()
    for diag in detected.values():
        for p in diag.role.pkgs:
            for tok in re.findall(r"[A-Za-z0-9_.-]+", p):
                if tok not in ("with", "pkgs", "override", "extensions", "rust-bin"):
                    known_role_pkgs.add(tok)

    extra_pkgs = sorted(list(flake_pkgs - known_role_pkgs))

    return list(detected.values()), extra_pkgs, channel


def diagnose_flake(
    project_root: Path,
    roles_db: dict[str, Role],
    aliases: dict[str, str],
) -> FlakeWorkspaceDiagnosis:
    """Performs full workspace diagnosis for active roles and configs."""
    flake_path = project_root / "flake.nix"
    if not flake_path.exists():
        return FlakeWorkspaceDiagnosis(project_root=project_root, flake_path=flake_path)

    try:
        content = flake_path.read_text(encoding="utf-8")
    except OSError:
        return FlakeWorkspaceDiagnosis(project_root=project_root, flake_path=flake_path)

    active_roles, extra_pkgs, channel = detect_active_roles(
        content, roles_db, aliases
    )

    # Detect workspace files
    discovered: list[str] = []
    for art_file, _ in KNOWN_PROJECT_ARTIFACTS:
        if (project_root / art_file).exists():
            discovered.append(art_file)

    return FlakeWorkspaceDiagnosis(
        project_root=project_root,
        flake_path=flake_path,
        channel=channel,
        active_roles=active_roles,
        extra_packages=extra_pkgs,
        discovered_artifacts=discovered,
    )


def display_active_roles(
    project_root: Path,
    roles_db: dict[str, Role],
    aliases: dict[str, str],
) -> None:
    """Renders formatted terminal diagnosis panel of active flake roles."""
    flake_path = project_root / "flake.nix"
    if not flake_path.exists():
        ui.error(f"No flake.nix found in {project_root} or its parent directories.")
        ui.info(
            f"Run '{ui.bold('basecamp init <roles...>')}' to bootstrap a reproducible DevShell.\n",
            symbol="💡",
        )
        return

    diag = diagnose_flake(project_root, roles_db, aliases)

    term_cols = shutil.get_terminal_size(fallback=(88, 24)).columns
    box_w = min(88, max(36, term_cols - 2))
    inner_w = box_w - 4
    sep_line = ui.dim("─" * inner_w)

    chan_str = diag.channel if diag.channel else ui.dim("custom / unspecified")

    panel_lines: list[str] = [
        f"{ui.bold('Workspace Root:')}  {diag.project_root}",
        f"{ui.bold('Flake Path:')}      {diag.flake_path}",
        f"{ui.bold('Nixpkgs Channel:')} {ui.cyan(chan_str)}",
        sep_line,
    ]

    if not diag.active_roles:
        panel_lines.append(
            ui.yellow("⚠️  No active Basecamp roles identified in flake.nix.")
        )
        if diag.extra_packages:
            panel_lines.append(
                f"{ui.bold('Detected Packages:')} {', '.join(diag.extra_packages[:8])}"
            )
        ui.panel("⛺  Basecamp Active Roles Diagnostic", panel_lines, width=box_w)
        ui.info(
            f"Run '{ui.bold('basecamp list')}' to see available roles, or '{ui.bold('basecamp shell <roles...>')}' to configure Basecamp roles.\n",
            symbol="💡",
        )
        return

    hdr_role = ui.bold(f"{'ROLE':<10}")
    hdr_cat = ui.bold(f"{'CATEGORY':<14}")
    hdr_desc = ui.bold("DESCRIPTION")

    panel_lines.append(
        f"{ui.bold('Active Roles:')}     {ui.bold_green(str(len(diag.active_roles)))} role(s) configured"
    )
    panel_lines.append(sep_line)
    panel_lines.append(f"{hdr_role}  {hdr_cat}  {hdr_desc}")
    panel_lines.append(sep_line)

    for r_diag in sorted(diag.active_roles, key=lambda x: x.role_key):
        r_col = ui.cyan(f"{r_diag.role_key:<10}")
        cat_col = f"{r_diag.role.category:<14}"
        panel_lines.append(f"{r_col}  {cat_col}  {r_diag.role.description}")

    if diag.discovered_artifacts:
        panel_lines.append(sep_line)
        arts_str = ", ".join(diag.discovered_artifacts[:6])
        if len(diag.discovered_artifacts) > 6:
            arts_str += f", +{len(diag.discovered_artifacts) - 6} more"
        panel_lines.append(f"{ui.bold('Workspace Files:')} {arts_str}")

    if diag.extra_packages:
        panel_lines.append(sep_line)
        pkgs_str = ", ".join(diag.extra_packages[:8])
        if len(diag.extra_packages) > 8:
            pkgs_str += f", +{len(diag.extra_packages) - 8} more"
        panel_lines.append(f"{ui.bold('Extra Packages:')}  {pkgs_str}")

    ui.panel("⛺  Basecamp Active Roles Diagnostic", panel_lines, width=box_w)
    ui.info(
        f"Run '{ui.bold('basecamp info <role>')}' for packages, hooks, and template files.\n",
        symbol="💡",
    )
