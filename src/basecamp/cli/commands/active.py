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
    unstable_channel: str | None = None
    active_roles: list[ActiveRoleDiagnostic] = field(default_factory=list)
    extra_packages: list[str] = field(default_factory=list)
    discovered_artifacts: list[str] = field(default_factory=list)


def _short_channel(url: str) -> str:
    """Reduces a standard nixpkgs flake URL to its branch name."""
    if "nixos-" in url or "nixpkgs-" in url:
        return url.split("/")[-1]
    return url


def detect_channels(flake_content: str) -> tuple[str | None, str | None]:
    """Returns (stable, unstable) channel names from the flake inputs."""
    stable = re.search(r'(?<![\w-])nixpkgs\.url\s*=\s*"([^"]+)";', flake_content)
    unstable = re.search(r'nixpkgs-unstable\.url\s*=\s*"([^"]+)";', flake_content)
    return (
        _short_channel(stable.group(1)) if stable else None,
        _short_channel(unstable.group(1)) if unstable else None,
    )


def _balanced_list(text: str, open_idx: int) -> str:
    """Returns the contents of the `[ ... ]` list starting at `open_idx`."""
    depth = 0
    for i in range(open_idx, len(text)):
        ch = text[i]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return text[open_idx + 1 : i]
    return text[open_idx + 1 :]


def extract_package_sets(flake_content: str) -> tuple[str, str]:
    """
    Extracts raw text of the stable and unstable package lists from the
    `packages = ...;` attribute. Supports both the dual-channel layout
    `(with pkgs; [..]) ++ (with unstable; [..])` and legacy `with pkgs; [..]`.
    """
    stable_parts: list[str] = []
    unstable_parts: list[str] = []
    head = re.search(r"\bpackages\s*=", flake_content)
    if not head:
        return "", ""
    pos = head.end()
    # Each group: optional `++`, optional `(`, then `with <scope>; [`.
    pattern = re.compile(r"\s*(?:\+\+\s*)?\(?\s*with\s+([\w-]+)\s*;\s*\[")
    while True:
        m = pattern.match(flake_content, pos)
        if not m:
            break
        open_idx = m.end() - 1
        body = _balanced_list(flake_content, open_idx)
        scope = m.group(1)
        (unstable_parts if scope == "unstable" else stable_parts).append(body)
        pos = open_idx + len(body) + 2
        # Skip the closing paren of a parenthesised group, if present.
        close = re.compile(r"\s*\)").match(flake_content, pos)
        if close:
            pos = close.end()
    return " ".join(stable_parts), " ".join(unstable_parts)


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
      3. Package signature matching from `(with pkgs; [...])` / `(with unstable; [...])`
    """
    detected: dict[str, ActiveRoleDiagnostic] = {}

    channel, _ = detect_channels(flake_content)

    # 1. Check explicit Basecamp roles metadata comment
    comment_match = re.search(
        r"#\s*\[basecamp\]\s*roles:\s*(.+)$",
        flake_content,
        re.MULTILINE | re.IGNORECASE,
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
    badge_matches = re.findall(r"\\033\[1m([^\\]+)\\033\[0m\s*\\033\[2m", flake_content)
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
                if hook and (
                    hook in flake_content or hook.splitlines()[0] in flake_content
                ):
                    detected[r_key] = ActiveRoleDiagnostic(
                        role_key=r_key,
                        role=role,
                        detection_method="hook",
                    )
                    break

    # 3. Extract packages lists (stable `with pkgs;` and unstable `with unstable;`)
    stable_raw, unstable_raw = extract_package_sets(flake_content)
    ignore_toks = ("with", "pkgs", "unstable", "override", "extensions", "rust-bin")

    def _tokens(raw: str) -> set[str]:
        # Drop quoted strings (e.g. withPackages names), then split identifiers.
        cleaned = re.sub(r'"[^"]*"', " ", raw)
        return {
            t for t in re.findall(r"[A-Za-z0-9_.-]+", cleaned) if t not in ignore_toks
        }

    stable_pkgs = _tokens(stable_raw)
    unstable_flake_pkgs = _tokens(unstable_raw)
    flake_pkgs: set[str] = stable_pkgs | unstable_flake_pkgs

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
        for p in diag.role.all_pkgs:
            for tok in re.findall(r"[A-Za-z0-9_.-]+", p):
                if tok not in ignore_toks:
                    known_role_pkgs.add(tok)

    # Unstable extras are reported with the `unstable.` prefix (CLI input syntax).
    extra_pkgs = sorted(
        [p for p in stable_pkgs - known_role_pkgs]
        + [f"unstable.{p}" for p in unstable_flake_pkgs - known_role_pkgs]
    )

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

    active_roles, extra_pkgs, channel = detect_active_roles(content, roles_db, aliases)
    _, unstable_channel = detect_channels(content)

    # Detect workspace files
    discovered: list[str] = []
    for art_file, _ in KNOWN_PROJECT_ARTIFACTS:
        if (project_root / art_file).exists():
            discovered.append(art_file)

    return FlakeWorkspaceDiagnosis(
        project_root=project_root,
        flake_path=flake_path,
        channel=channel,
        unstable_channel=unstable_channel,
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
        if ui.is_json:
            ui.json(
                {
                    "status": "error",
                    "error": f"No flake.nix found in {project_root} or its parent directories.",
                    "project_root": str(project_root),
                }
            )
            return
        ui.error(f"No flake.nix found in {project_root} or its parent directories.")
        if not ui.is_agent:
            ui.info(
                f"Run '{ui.bold('basecamp init <roles...>')}' to bootstrap a reproducible DevShell.\n",
                symbol="💡",
            )
        return

    diag = diagnose_flake(project_root, roles_db, aliases)

    if ui.is_json:
        data = {
            "status": "ok",
            "project_root": str(diag.project_root),
            "flake_path": str(diag.flake_path),
            "channel": diag.channel,
            "unstable_channel": diag.unstable_channel,
            "active_roles": [
                {
                    "role": r.role_key,
                    "category": r.role.category,
                    "description": r.role.description,
                    "detection_method": r.detection_method,
                }
                for r in diag.active_roles
            ],
            "extra_packages": diag.extra_packages,
            "discovered_artifacts": diag.discovered_artifacts,
        }
        ui.json(data)
        return

    term_cols = shutil.get_terminal_size(fallback=(88, 24)).columns
    box_w = min(88, max(36, term_cols - 2))
    inner_w = box_w - 4
    sep_line = ui.dim("─" * inner_w)

    chan_str = diag.channel if diag.channel else ui.dim("custom / unspecified")
    unstable_str = (
        diag.unstable_channel if diag.unstable_channel else ui.dim("none (legacy flake)")
    )

    panel_lines: list[str] = [
        f"{ui.bold('Workspace Root:')}  {diag.project_root}",
        f"{ui.bold('Flake Path:')}      {diag.flake_path}",
        f"{ui.bold('Nixpkgs Channel:')} {ui.cyan(chan_str)}",
        f"{ui.bold('Unstable Input:')}  {ui.cyan(unstable_str)}",
        sep_line,
    ]

    if not diag.active_roles:
        panel_lines.append(
            ui.yellow("No active Basecamp roles identified in flake.nix.")
            if ui.is_agent
            else ui.yellow("⚠️  No active Basecamp roles identified in flake.nix.")
        )
        if diag.extra_packages:
            panel_lines.append(
                f"{ui.bold('Detected Packages:')} {', '.join(diag.extra_packages[:8])}"
            )
        ui.panel("Basecamp Active Roles Diagnostic", panel_lines, width=box_w)
        if not ui.is_agent:
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

    ui.panel("Basecamp Active Roles Diagnostic", panel_lines, width=box_w)
    if not ui.is_agent:
        ui.info(
            f"Run '{ui.bold('basecamp info <role>')}' for packages, hooks, and template files.\n",
            symbol="💡",
        )
