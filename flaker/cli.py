import os
import shutil
import subprocess
import sys
import time
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

from flaker import __version__
from flaker.ui import ui


@dataclass
class Role:
    pkgs: list[str]
    hooks: list[str]
    category: str = "General"
    description: str = ""
    ignores: list[str] = field(default_factory=list)
    targets: dict[str, dict[str, Any]] = field(default_factory=dict)


def get_project_name(root_path: Path) -> str:
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


def fmt_status(icon: str, name: str, detail: str = "") -> str:
    """Formats shell status messages with ANSI colors and icons."""
    extra = f" ({detail})" if detail else ""
    return (
        f"printf '\\033[1;34m❄️  [flaker]\\033[0m {icon} "
        f"\\033[1m{name}\\033[0m{extra} active\\n'"
    )


def build_builtin_role_registry(folder_name: str) -> dict[str, Role]:
    return {
        # ------------------------------------------------------------
        # Systems & Compiled Languages
        # ------------------------------------------------------------
        "rust": Role(
            category="Systems",
            description="Stable toolchain + rust-analyzer + lldb",
            pkgs=[
                '(rust-bin.stable.latest.default.override { extensions = [ "rust-analyzer" ]; })',
                "cargo-expand",
                "lldb",
            ],
            hooks=[
                f"[ -f Cargo.toml ] || cargo init --name {folder_name}",
                fmt_status("🦀", "Rust", "stable toolchain + rust-analyzer"),
            ],
            ignores=["target/", "**/*.rs.bk"],
        ),
        "c": Role(
            category="Systems",
            description="GCC/Clang + clangd + cmake + ninja",
            pkgs=[
                "gcc",
                "gdb",
                "cmake",
                "pkg-config",
                "gnumake",
                "ninja",
                "clang-tools",
            ],
            hooks=[fmt_status("⚡", "C", "GCC/Clang + clangd")],
            ignores=[
                "build/",
                "bin/",
                "*.o",
                "*.a",
                "*.so",
                "compile_commands.json",
                ".cache/",
            ],
        ),
        "cpp": Role(
            category="Systems",
            description="GCC/Clang + clangd + cmake + ninja",
            pkgs=[
                "gcc",
                "gdb",
                "cmake",
                "pkg-config",
                "gnumake",
                "ninja",
                "clang-tools",
            ],
            hooks=[fmt_status("⚡", "C++", "GCC/Clang + clangd")],
            ignores=[
                "build/",
                "bin/",
                "*.o",
                "*.a",
                "*.so",
                "compile_commands.json",
                ".cache/",
            ],
        ),
        "go": Role(
            category="Systems",
            description="Go toolchain + gopls + delve",
            pkgs=[
                "go",
                "gopls",
                "gotools",
                "golangci-lint",
                "delve",
            ],
            hooks=[
                f"[ -f go.mod ] || go mod init {folder_name}",
                fmt_status("🐹", "Go", "Go toolchain + gopls"),
            ],
            ignores=["bin/", "dist/"],
        ),
        "zig": Role(
            category="Systems",
            description="Zig compiler + zls LSP",
            pkgs=[
                "zig",
                "zls",
            ],
            hooks=[
                fmt_status("⚡", "Zig", "Zig toolchain + zls"),
            ],
            ignores=["zig-cache/", "zig-out/"],
        ),
        "java": Role(
            category="Systems",
            description="OpenJDK 25 + jdtls + maven/gradle",
            pkgs=[
                "jdk25",
                "jdt-language-server",
                "google-java-format",
                "maven",
                "gradle",
            ],
            hooks=[
                'export JAVA_HOME="${pkgs.jdk25}/lib/openjdk"',
                fmt_status("☕", "Java", "JDK 25 + jdtls"),
            ],
            ignores=["target/", ".gradle/", "build/"],
        ),
        "dotnet": Role(
            category="Systems",
            description=".NET 9 SDK + Omnisharp",
            pkgs=[
                "dotnet-sdk_9",
                "omnisharp-roslyn",
            ],
            hooks=[
                'export DOTNET_ROOT="${pkgs.dotnet-sdk_9}"',
                fmt_status("🔷", ".NET", ".NET 9 SDK + Omnisharp"),
            ],
            ignores=["bin/", "obj/"],
        ),
        # ------------------------------------------------------------
        # Scripting, Data & Scientific
        # ------------------------------------------------------------
        "python": Role(
            category="Data & Scientific",
            description="Python 3.14 + uv + ruff + ty",
            pkgs=[
                "python314",
                "uv",
                "ruff",
                "ty",
            ],
            hooks=[
                'export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"',
                "export UV_PYTHON_DOWNLOADS=never",
                "[ -f pyproject.toml ] && uv sync",
                (
                    "[ -f requirements.txt ] && [ ! -d .venv ] && "
                    "uv venv && uv pip install -r requirements.txt"
                ),
                "[ -d .venv ] && source .venv/bin/activate",
                fmt_status("🐍", "Python", "uv + ruff + ty"),
            ],
            ignores=[
                "__pycache__/",
                "*.py[cod]",
                ".venv/",
                ".ruff_cache/",
                "dist/",
                "build/",
                "*.egg-info/",
            ],
        ),
        "mathvis": Role(
            category="Data & Scientific",
            description="Python 3.14 + scientific computation stack",
            pkgs=[
                "python314",
                "uv",
                "ruff",
                "ty",
            ],
            hooks=[
                'export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"',
                "export UV_PYTHON_DOWNLOADS=never",
                "[ -f pyproject.toml ] && uv sync",
                "[ -d .venv ] && source .venv/bin/activate",
                fmt_status("📐", "Mathvis", "πthon 3.14 + Scientific Stack"),
            ],
            ignores=[
                "__pycache__/",
                "*.py[cod]",
                ".venv/",
                ".ruff_cache/",
                "dist/",
                "build/",
            ],
        ),
        "julia": Role(
            category="Data & Scientific",
            description="Julia S&C + Formatter",
            pkgs=[
                '(julia-bin.withPackages [ "ControlSystems" "DifferentialEquations" "GLMakie" "CairoMakie" "LanguageServer" ])',
                "julia-formatter",
            ],
            hooks=[fmt_status("🔵", "Julia", "Julia S&C + Formatter")],
            ignores=[],
        ),
        # ------------------------------------------------------------
        # Web & Frontend Ecosystem
        # ------------------------------------------------------------
        "ts": Role(
            category="Web & Frontend",
            description="TypeScript/JS + Bun + vtsls + prettierd",
            pkgs=["bun", "vtsls", "typescript", "prettierd"],
            hooks=[fmt_status("🟦", "JS/TS", "Bun + vtsls + prettierd")],
            ignores=["node_modules/", "dist/"],
        ),
        "svelte": Role(
            category="Web & Frontend",
            description="Svelte 5 + Bun + svelte-ls",
            pkgs=[
                "bun",
                "svelte-language-server",
                "vtsls",
                "typescript",
                "prettierd",
            ],
            hooks=[
                "[ -f package.json ] || bun create svelte@latest .",
                fmt_status("🟧", "Svelte 5", "Bun + svelte-ls"),
            ],
            ignores=["node_modules/", ".svelte-kit/", "build/"],
        ),
        "vue": Role(
            category="Web & Frontend",
            description="Vue + Bun + vue-ls",
            pkgs=[
                "bun",
                "vue-language-server",
                "vtsls",
                "typescript",
                "prettierd",
            ],
            hooks=[
                "[ -f package.json ] || bun create vue@latest",
                fmt_status("🟢", "Vue", "Bun + vue-ls"),
            ],
            ignores=["node_modules/", "dist/"],
        ),
        "next": Role(
            category="Web & Frontend",
            description="Next.js + Bun + vtsls",
            pkgs=[
                "bun",
                "vtsls",
                "typescript",
                "prettierd",
            ],
            hooks=[
                "[ -f package.json ] || bun create next-app",
                fmt_status("⚛️ ", "Next.js", "Bun + vtsls"),
            ],
            ignores=["node_modules/", ".next/", "out/"],
        ),
        # ------------------------------------------------------------
        # Functional Ecosystem
        # ------------------------------------------------------------
        "gleam": Role(
            category="Functional",
            description="Gleam + Erlang runtime + rebar3",
            pkgs=["gleam", "erlang", "rebar3"],
            hooks=[
                fmt_status("🌸", "Gleam", "Gleam + Erlang runtime"),
            ],
            ignores=["build/"],
        ),
        "elixir": Role(
            category="Functional",
            description="Elixir + Mix + elixir-ls",
            pkgs=["elixir", "elixir-ls"],
            hooks=[
                fmt_status("💧", "Elixir", "Elixir + Mix + elixir-ls"),
            ],
            ignores=["_build/", "deps/"],
        ),
        "haskell": Role(
            category="Functional",
            description="GHC + Cabal + HLS + Ormolu",
            pkgs=[
                "ghc",
                "cabal-install",
                "haskell-language-server",
                "hlint",
                "ormolu",
            ],
            hooks=[
                fmt_status("λ ", "Haskell", "GHC + Cabal + HLS + Ormolu"),
            ],
            ignores=["dist-newstyle/", ".cabal-sandbox/"],
        ),
        # ------------------------------------------------------------
        # Document & Typesetting Workspaces (Unified under Folio)
        # ------------------------------------------------------------
        "folio": Role(
            category="Typesetting",
            description="Polyglot Document Engine (Typst + LaTeX + Markdown)",
            pkgs=[
                "typst",
                "pandoc",
                "tinymist",
                "typstyle",
                "tectonic",
                "texlab",
            ],
            hooks=[
                'export TYPST_ROOT="$PWD"',
                fmt_status("📝", "Folio", "Polyglot Document Engine (Typst + LaTeX)"),
            ],
            ignores=[
                "*.aux",
                "*.log",
                "*.out",
                "*.toc",
                "*.synctex.gz",
                "*.fdb_latexmk",
                "*.fls",
            ],
            targets={
                # --------------------------------------------------------
                # 1. Polyglot Markdown Workspaces (Frontmatter driven)
                # --------------------------------------------------------
                "report": {
                    "project": ["packages.typ", "report.typ", "library.bib"],
                    "starter": ["report.md"],
                    "description": "Polyglot Markdown report (report.md + packages + library.bib)",
                    "aliases": ["md-report", "doc", "document", "default"],
                },
                "slides": {
                    "project": ["packages.typ", "slides.typ", "library.bib"],
                    "starter": ["slides.md"],
                    "description": "Polyglot Markdown 16:9 slides (slides.md + packages + library.bib)",
                    "aliases": ["md-slides", "presentation", "slodes", "slide", "deck", "ppt"],
                },
                "paper": {
                    "project": ["packages.typ", "paper.typ", "library.bib"],
                    "starter": ["paper.md"],
                    "description": "Polyglot Markdown IEEE paper (paper.md + packages + library.bib)",
                    "aliases": ["md-paper", "ieee", "article"],
                },
                # --------------------------------------------------------
                # 2. Native Typst Workspaces
                # --------------------------------------------------------
                "typst-report": {
                    "project": ["packages.typ", "library.bib"],
                    "starter": ["report.typ"],
                    "description": "Native Typst technical report (report.typ + packages.typ + library.bib)",
                    "aliases": ["typ-report"],
                },
                "typst-slides": {
                    "project": ["packages.typ", "library.bib"],
                    "starter": ["slides.typ"],
                    "description": "Native Typst 16:9 presentation (slides.typ + packages.typ + library.bib)",
                    "aliases": ["typ-slides"],
                },
                "typst-paper": {
                    "project": ["packages.typ", "library.bib"],
                    "starter": ["paper.typ"],
                    "description": "Native Typst IEEE 2-column paper (paper.typ + packages.typ + library.bib)",
                    "aliases": ["typ-paper", "typst", "typ"],
                },
                # --------------------------------------------------------
                # 3. Native LaTeX Workspaces
                # --------------------------------------------------------
                "latex-report": {
                    "project": ["packages.tex", "library.bib"],
                    "starter": ["report.tex"],
                    "description": "Native LaTeX technical report (report.tex + packages.tex + library.bib)",
                    "aliases": ["tex-report"],
                },
                "latex-slides": {
                    "project": ["packages.tex", "library.bib"],
                    "starter": ["slides.tex"],
                    "description": "Native LaTeX 16:9 Beamer slides (slides.tex + packages.tex + library.bib)",
                    "aliases": ["tex-slides", "beamer"],
                },
                "latex-paper": {
                    "project": ["packages.tex", "library.bib"],
                    "starter": ["paper.tex"],
                    "description": "Native LaTeX IEEEtran paper (paper.tex + packages.tex + library.bib)",
                    "aliases": ["tex-paper", "latex", "tex"],
                },
            },
        ),
        # ------------------------------------------------------------
        # Cloud & Infrastructure
        # ------------------------------------------------------------
        "ops": Role(
            category="DevOps & Cloud",
            description="Docker Compose + Lazydocker + K8s tooling",
            pkgs=[
                "docker-compose",
                "lazydocker",
                "kubectl",
                "kubernetes-helm",
                "k9s",
                "dive",
            ],
            hooks=[
                fmt_status("🐳", "DevOps", "Docker + K8s tooling"),
            ],
            ignores=[],
        ),
    }


BUILTIN_ALIASES = {
    "py": "python",
    "rs": "rust",
    "react": "next",
    "js": "ts",
    "mv": "mathvis",
    "md": "folio:report",
    "typ": "folio:typst-report",
    "typst": "folio:typst-report",
    "typst-paper": "folio:typst-paper",
    "typst-report": "folio:typst-report",
    "typst-slides": "folio:typst-slides",
    "typst:paper": "folio:typst-paper",
    "typst:report": "folio:typst-report",
    "typst:slides": "folio:typst-slides",
    "typ-paper": "folio:typst-paper",
    "typ-report": "folio:typst-report",
    "typ-slides": "folio:typst-slides",
    "typ:paper": "folio:typst-paper",
    "typ:report": "folio:typst-report",
    "typ:slides": "folio:typst-slides",
    "tex": "folio:latex-report",
    "latex": "folio:latex-report",
    "latex-paper": "folio:latex-paper",
    "latex-report": "folio:latex-report",
    "latex-slides": "folio:latex-slides",
    "latex:paper": "folio:latex-paper",
    "latex:report": "folio:latex-report",
    "latex:slides": "folio:latex-slides",
    "tex-report": "folio:latex-report",
    "tex-slides": "folio:latex-slides",
    "tex-paper": "folio:latex-paper",
    "tex:report": "folio:latex-report",
    "tex:slides": "folio:latex-slides",
    "tex:paper": "folio:latex-paper",
    "beamer": "folio:latex-slides",
    "hs": "haskell",
    "cs": "dotnet",
    "csharp": "dotnet",
    "devops": "ops",
    "docker": "ops",
    "ex": "elixir",
    "slides": "folio:slides",
    "presentation": "folio:slides",
    "paper": "folio:paper",
    "report": "folio:report",
    "md-report": "folio:report",
    "md-slides": "folio:slides",
    "md-paper": "folio:paper",
    "md:report": "folio:report",
    "md:slides": "folio:slides",
    "md:paper": "folio:paper",
}


def load_user_config() -> tuple[dict[str, Role], dict[str, str], list[Path]]:
    """Loads custom roles, aliases, and templates from ~/.config/flaker/roles.toml."""
    config_dir = (
        Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "flaker"
    )
    roles_file = config_dir / "roles.toml"
    extra_roles: dict[str, Role] = {}
    extra_aliases: dict[str, str] = {}
    custom_asset_dirs: list[Path] = [config_dir / "templates"]

    if roles_file.exists():
        try:
            with open(roles_file, "rb") as f:
                data = tomllib.load(f)
            for role_key, role_data in data.get("roles", {}).items():
                extra_roles[role_key] = Role(
                    pkgs=role_data.get("pkgs", []),
                    hooks=role_data.get("hooks", []),
                    category=role_data.get("category", "Custom"),
                    description=role_data.get("description", "Custom user role"),
                    ignores=role_data.get("ignores", []),
                    targets=role_data.get("targets", {}),
                )
            for alias_key, target_role in data.get("aliases", {}).items():
                extra_aliases[alias_key] = target_role
        except Exception as e:
            ui.warn(f"Failed to parse user config at {roles_file}: {e}")

    return extra_roles, extra_aliases, custom_asset_dirs


def resolve_nixpkgs_url(channel: str | None) -> str:
    """Translates a channel alias or full URL into a flake-compatible nixpkgs URL."""
    if not channel or channel in ("26.05", "nixos-26.05"):
        return "github:NixOS/nixpkgs/nixos-26.05"
    if channel in ("unstable", "nixpkgs-unstable"):
        return "github:NixOS/nixpkgs/nixpkgs-unstable"
    if channel == "nixos-unstable":
        return "github:NixOS/nixpkgs/nixos-unstable"
    if channel.startswith("github:") or channel.startswith("git+") or "/" in channel:
        return channel
    return f"github:NixOS/nixpkgs/nixos-{channel}"


def print_help():
    """Prints the CLI usage instructions."""
    print(f"""{ui.badge()} {ui.bold("Polyglot Nix Flake DevShell & Scaffolding Engine")}

{ui.blue("Usage:")}
  flaker [options]
  flaker <command> [roles...] [options]

{ui.blue("Commands:")}
  init         Create full setup (flake, envrc, project configs, starter).
  new          Add starter file (main.py, report.md, etc.).
  shell        Add flake.nix and .envrc.
  project      Add project configs (pyproject.toml, packages.typ, etc.).
  packages     Configure package bundles.
  list         List available roles and stacks.
  info <role>  Display detailed information for a role.
  interactive  Launch interactive stack and command selector.

{ui.blue("Options:")}
  -m, --mode MODE      Document operating mode / target (report, slides, paper).
  -t, --target TARGET  Alias for --mode.
  -e, --engine ENGINE  Compilation engine for Markdown ('typst' or 'latex').
  -p, --packages       Configure packages dynamically (default in interactive mode).
  --no-pkg             Skip interactive package bundle selection.
  --no-packages        Alias for --no-pkg.
  --title TITLE        Document title for Folio documents.
  --author AUTHOR      Document author for Folio documents.
  --theme THEME        Presentation theme for slides ('dark' or 'light').
  -f, --force          Overwrite existing files without confirmation prompts.
  -n, --dry-run        Preview generated files in stdout without writing.
  -c, --channel NAME   Nixpkgs channel (default: nixos-26.05, e.g. unstable, 24.11).
  --no-direnv          Skip generating .envrc and skip 'direnv allow'.
  --no-git             Do not automatically stage generated files with 'git add'.
  --color MODE         Color output mode: auto, always, never (default: auto).
  --no-color           Disable colored output.
  -h, --help           Show this help message and exit.
  -V, -v, --version    Show version and exit.

{ui.blue("Examples:")}
  flaker                                 # Interactive Bun-style stack selector
  flaker init py                         # Setup Python DevShell, root configs, and starter
  flaker init py cpp rust typ            # Polyglot multi-language workspace bootstrap
  flaker init folio report               # Setup Folio workspace for clean report document
  flaker init folio slides               # Setup Folio workspace for 16:9 presentation slides
  flaker init folio paper                # Setup Folio workspace for IEEE 2-column paper
  flaker init folio slides --packages    # Scaffold slides and interactively pick package bundles
  flaker packages typ                    # Interactively configure Typst packages (packages.typ)
  flaker packages tex                    # Interactively configure LaTeX packages (packages.tex)
  flaker init typ                        # Setup native Typst workspace (report.typ + packages.typ)
  flaker init tex                        # Setup native LaTeX workspace (report.tex + packages.tex)
  flaker new md:slides                   # Drop slides.md in current folder
  flaker new typ:paper                   # Drop native Typst IEEE 2-column paper (paper.typ)
  flaker new tex:slides                  # Drop native LaTeX Beamer presentation (slides.tex)
  flaker new paper                       # Direct shortcut to drop paper.md in current folder
  flaker init folio -m slides            # Bootstrap slides using explicit --mode flag
  flaker new mv                          # Drop mathvis plot.py in current experiment folder
  flaker new typ                         # Drop native Typst report (report.typ) in current folder
  flaker shell rust next                 # Setup DevShell without scaffolding files
  flaker project folio                   # Scaffold layout templates & library.bib to project root
  flaker list                            # View all registered language roles & aliases
""")


def display_roles_list(roles_db: dict[str, Role], aliases: dict[str, str]) -> None:
    """Prints a clean, formatted terminal table of all registered roles inside a ui.panel."""
    # Group roles by category
    categories: dict[str, list[str]] = {}
    for r_key, role in roles_db.items():
        categories.setdefault(role.category, []).append(r_key)

    term_cols = shutil.get_terminal_size(fallback=(88, 24)).columns
    box_w = min(88, max(36, term_cols - 2))
    inner_w = box_w - 4

    hdr_role = ui.bold(f"{'ROLE':<10}")
    hdr_cat = ui.bold(f"{'CATEGORY':<18}")
    hdr_desc = ui.bold("DESCRIPTION")
    sep_line = ui.dim("─" * inner_w)

    panel_lines: list[str] = [
        f"{hdr_role}  {hdr_cat}  {hdr_desc}",
        sep_line,
    ]

    for cat in sorted(categories.keys()):
        for r_key in sorted(categories[cat]):
            role = roles_db[r_key]
            r_col = ui.cyan(f"{r_key:<10}")
            cat_col = f"{role.category:<18}"
            panel_lines.append(f"{r_col}  {cat_col}  {role.description}")

    ui.panel("❄️  Flaker Roles Registry", panel_lines, width=box_w)
    ui.info(
        f"Run '{ui.bold('flaker info <role>')}' for packages, hooks, and starter files.\n",
        symbol="💡",
    )


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
            f"Unknown role '{role_name}'. Run 'flaker list' to see available roles."
        )
        sys.exit(1)

    role = roles_db[resolved_name]
    # Only direct role aliases (exclude target shortcuts like folio:slides)
    rev_aliases = [
        a for a, t in aliases.items() if t == resolved_name
    ]

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
            print(f"\n  {ui.bold('Project Root Foundation Files (flaker project):')}")
            for pf in project_files:
                print(f"    📦 {ui.cyan(pf)}")

        if starter_files:
            print(f"\n  {ui.bold('Starter / Leaf Files (flaker new):')}")
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
            existing_lines.update(missing_frost)  # Deduplicate

    # 2. Base Nix & Direnv rules
    base_rules = [".direnv/", "result", "result-*"]
    missing_base = [r for r in base_rules if r not in existing_lines]
    if missing_base:
        new_sections.append("# Nix & Direnv\n" + "\n".join(missing_base))
        existing_lines.update(missing_base)  # Deduplicate

    # 3. Role-specific rules
    for r in resolved_roles:
        if r in roles_db and roles_db[r].ignores:
            missing = [ign for ign in roles_db[r].ignores if ign not in existing_lines]
            if missing:
                new_sections.append(
                    f"# {roles_db[r].category} ({r})\n" + "\n".join(missing)
                )
                existing_lines.update(missing)  # Deduplicate

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


def stage_git_files(project_root: Path, files: list[str]):
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
        subprocess.run(["direnv", "allow"], cwd=project_root, check=False)

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


def resolve_role_target(
    role_key: str, target_input: str, roles_db: dict[str, Role]
) -> str | None:
    """Resolves target_input against role's target definitions or returns None."""
    if role_key not in roles_db:
        return None
    role = roles_db[role_key]
    if not role.targets:
        return None
    t_clean = target_input.strip().lower()
    for canonical_name, meta in role.targets.items():
        if t_clean == canonical_name.lower():
            return canonical_name
        aliases = [a.lower() for a in meta.get("aliases", [])]
        if t_clean in aliases:
            return canonical_name
    return None


def find_role_for_standalone_target(
    target_input: str, roles_db: dict[str, Role]
) -> tuple[str, str] | None:
    """
    Checks if target_input is a valid target for any role with targets.
    Returns (role_key, canonical_target_name) or None.
    """
    for role_key, role in roles_db.items():
        if role.targets:
            canonical = resolve_role_target(role_key, target_input, roles_db)
            if canonical:
                return role_key, canonical
    return None


def get_git_author() -> str:
    """Retrieves git user.name if configured."""
    try:
        res = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return ""


TYPST_PACKAGE_BUNDLES: list[dict[str, Any]] = [
    {
        "id": "cetz",
        "label": "CeTZ (@preview/cetz:0.5.2)",
        "desc": "TikZ-like vector drawing canvas & scientific plotting engine",
        "default": True,
        "snippet": (
            "// --- 1. Vector Drawing & Graphing (The \"TikZ\" of Typst) ---\n"
            "// CeTZ provides a comprehensive TikZ-inspired vector canvas\n"
            '#import "@preview/cetz:0.5.2"\n'
        ),
    },
    {
        "id": "fletcher",
        "label": "Fletcher (@preview/fletcher:0.5.8)",
        "desc": "Commutative diagrams, finite state machines, and flowcharts",
        "default": True,
        "snippet": (
            "// Fletcher provides elegant commutative diagrams and state machines\n"
            '#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge\n'
        ),
    },
    {
        "id": "physica",
        "label": "Physica (@preview/physica:0.9.8)",
        "desc": "Advanced math, differential forms, matrices, and bra-kets",
        "default": True,
        "snippet": (
            "// --- 2. Advanced Mathematics & Physics Notation ---\n"
            "// Mathematica/Physics notation: differential forms, matrices, bra-kets\n"
            '#import "@preview/physica:0.9.8": *\n'
        ),
    },
    {
        "id": "mitex",
        "label": "MiTeX (@preview/mitex:0.2.7)",
        "desc": "Compile native LaTeX math equations directly inside Typst blocks",
        "default": False,
        "snippet": (
            "// MiTeX allows writing native LaTeX equations directly inside Typst blocks\n"
            '#import "@preview/mitex:0.2.7": mitex\n'
        ),
    },
    {
        "id": "merman",
        "label": "Merman (@preview/merman:0.1.0)",
        "desc": "Native Mermaid renderer for software flowcharts, sequences & ERDs",
        "default": True,
        "snippet": (
            "// --- 3. Flowcharts & Software Architecture Diagrams ---\n"
            "// Native Mermaid renderer for software flowcharts, sequences, and classes\n"
            '#import "@preview/merman:0.1.0": mermaid\n'
        ),
    },
    {
        "id": "tablex",
        "label": "Tablex (@preview/tablex:0.0.9)",
        "desc": "Publication-grade tables with custom colspans, rowspans & cell styling",
        "default": True,
        "snippet": (
            "// --- 4. Advanced Tables & Data Grids ---\n"
            "// Publication-grade table styling, custom colspans, rowspans, and cell styling\n"
            '#import "@preview/tablex:0.0.9": tablex, cellx, hlinex, vlinex\n'
        ),
    },
    {
        "id": "algorithmic",
        "label": "Algorithmic (@preview/algorithmic:1.0.7)",
        "desc": "Clean pseudocode typesetting with line numbering and indentation",
        "default": False,
        "snippet": (
            "// --- 5. Algorithmic Pseudocode ---\n"
            "// Clean pseudocode typesetting with line numbering and indentation\n"
            '#import "@preview/algorithmic:1.0.7": *\n'
        ),
    },
    {
        "id": "codly",
        "label": "Codly (@preview/codly:1.3.0)",
        "desc": "Enhanced source code blocks with line numbering and tab labels",
        "default": False,
        "snippet": (
            "// --- 6. Code Block Formatting (Codly) ---\n"
            "// Enhanced code blocks with line numbering, icons, and tab labels\n"
            '#import "@preview/codly:1.3.0": *\n'
        ),
    },
]

LATEX_PACKAGE_BUNDLES: list[dict[str, Any]] = [
    {
        "id": "typography",
        "label": "Typography & Fonts",
        "desc": "Fontspec, TeX Gyre Pagella, JetBrains Mono, Babel, Microtype",
        "default": True,
        "snippet": (
            "% --- 1. Core Typography, Fonts & Localization ---\n"
            "\\usepackage{fontspec}\n"
            "\\setmainfont{TeX Gyre Pagella}\n"
            "\\setmonofont{JetBrainsMono NFM}\n"
            "\\usepackage[english]{babel}\n"
            "\\usepackage{microtype}                  % Improved kerning and micro-typography\n"
            "\\providecommand{\\tightlist}{\\setlength{\\itemsep}{0pt}\\setlength{\\parskip}{0pt}}\n"
        ),
    },
    {
        "id": "math",
        "label": "Mathematics & Physics",
        "desc": "AMS-LaTeX, mathtools, bm, diffcoeff, siunitx",
        "default": True,
        "snippet": (
            "% --- 2. Mathematical Sciences & Physics ---\n"
            "\\usepackage{amsmath, amssymb, amsfonts} % Core AMS mathematical symbols & environments\n"
            "\\usepackage{mathtools}                  % Mathematical tools and extensions\n"
            "\\usepackage{bm}                         % Bold mathematical symbols (\\bm{\\alpha})\n"
            "\\usepackage{diffcoeff}                  % Clean derivative notation (\\diff{y}{x})\n"
            "\\usepackage{siunitx}                    % Comprehensive SI units formatting (\\qty{10}{\\meter\\per\\second})\n"
        ),
    },
    {
        "id": "tikz",
        "label": "TikZ & PGFPlots (Vector Graphics)",
        "desc": "TikZ, PGFPlots 1.18, arrows.meta, positioning, calc, tikz-cd",
        "default": True,
        "snippet": (
            "% --- 3. Vector Graphics, Plotting & Diagramming (TikZ) ---\n"
            "\\usepackage{graphicx}                   % Figure & image inclusion\n"
            "\\usepackage{xcolor}                     % Color model support\n"
            "\\usepackage{tikz}                       % TikZ vector drawing engine\n"
            "\\usetikzlibrary{\n"
            "  arrows.meta,                          % Modern arrow heads\n"
            "  positioning,                          % Relative node placement\n"
            "  calc,                                 % Coordinate calculations\n"
            "  shapes.geometric,                     % Advanced shapes\n"
            "  fit,                                  % Bounding box fitting\n"
            "  backgrounds                           % Background layers\n"
            "}\n"
            "\\usepackage{pgfplots}                   % High-quality scientific plotting\n"
            "\\pgfplotsset{compat=1.18}\n"
            "\\usepackage{tikz-cd}                    % Commutative & architecture flow diagrams\n"
        ),
    },
    {
        "id": "tables",
        "label": "Academic Tables & Structure",
        "desc": "Booktabs, tabularx, multirow, makecell, array, enumitem",
        "default": True,
        "snippet": (
            "% --- 4. Academic Tables & Structural Layout ---\n"
            "\\usepackage{booktabs}                   % Publication-quality horizontal rules\n"
            "\\usepackage{longtable}                  % Multi-page tables generated by Markdown/Pandoc\n"
            "\\usepackage{tabularx}                   % Tables with auto-expanding columns\n"
            "\\usepackage{multirow}                   % Multi-row table cells\n"
            "\\usepackage{makecell}                   % Flexible column headers & multi-line cells\n"
            "\\usepackage{array}                      % Extended array and tabular environments\n"
            "\\makeatletter\n"
            "\\@ifclassloaded{beamer}{}{\\usepackage{enumitem}}\n"
            "\\makeatother\n"
        ),
    },
    {
        "id": "boxes",
        "label": "Code Listings & Callouts",
        "desc": "Listings, tcolorbox with skins & breakable",
        "default": True,
        "snippet": (
            "% --- 5. Code Listings & Callout Containers ---\n"
            "\\usepackage{listings}                   % Source code syntax highlighting\n"
            "\\usepackage{tcolorbox}                  % Sleek modern callout frames & boxes\n"
            "\\tcbuselibrary{skins, breakable}\n"
        ),
    },
    {
        "id": "refs",
        "label": "Citations & Cross-Referencing",
        "desc": "Cite, ulem, hyperref, cleveref",
        "default": True,
        "snippet": (
            "% --- 6. Citations, Hyperlinks & Cross-Referencing ---\n"
            "\\usepackage{cite}                       % Standard numeric citation formatting\n"
            "\\usepackage[normalem]{ulem}             % Sophisticated underlining\n"
            "\\usepackage{hyperref}                   % Clickable hyper-links & PDF bookmarks\n"
            "\\hypersetup{\n"
            "  colorlinks=true,\n"
            "  linkcolor=blue!70!black,\n"
            "  citecolor=green!50!black,\n"
            "  urlcolor=blue!80!black\n"
            "}\n"
            "\\usepackage{cleveref}                   % Intelligent contextual references (\\cref{fig:model})\n"
        ),
    },
]


def generate_packages_manifest(
    pkg_type: str = "typst",
    selected_ids: Sequence[str] | None = None,
) -> str:
    """Generates a dynamic package manifest text for Typst or LaTeX."""
    is_typst = pkg_type in ("typst", "typ")
    bundles = TYPST_PACKAGE_BUNDLES if is_typst else LATEX_PACKAGE_BUNDLES

    if selected_ids is None:
        selected_set = {b["id"] for b in bundles if b.get("default", False)}
    else:
        selected_set = set(selected_ids)

    lines = []
    if is_typst:
        lines.append("// ========================================================")
        lines.append("// MODULAR TYPST PACKAGE MANIFEST (packages.typ)")
        lines.append("// Dynamically generated by Flaker")
        lines.append("// ========================================================\n")
    else:
        lines.append("% ========================================================")
        lines.append("% MODULAR LATEX PACKAGE MANIFEST (packages.tex)")
        lines.append("% Dynamically generated by Flaker")
        lines.append("% ========================================================\n")

    for bundle in bundles:
        if bundle["id"] in selected_set:
            lines.append(bundle["snippet"].strip())
            lines.append("")

    return "\n".join(lines).strip() + "\n"


def configure_packages_interactive(
    preferred_type: str | None = None,
    dest_dir: Path | None = None,
) -> Path | None:
    """
    Interactively configures and dynamically generates packages.typ or packages.tex
    using ui.multiselect with sane defaults preselected.
    """
    target_dir = dest_dir or Path.cwd()

    # Infer package type if not explicitly passed
    pkg_type = preferred_type
    if not pkg_type:
        has_typ = (target_dir / "packages.typ").exists() or list(target_dir.glob("*.typ"))
        has_tex = (target_dir / "packages.tex").exists() or list(target_dir.glob("*.tex"))
        if has_typ and not has_tex:
            pkg_type = "typst"
        elif has_tex and not has_typ:
            pkg_type = "latex"
        elif sys.stdin.isatty():
            pkg_type = ui.select(
                "Select package manifest to configure:",
                [
                    ("typst", "Typst package manifest (packages.typ)"),
                    ("latex", "LaTeX package manifest (packages.tex)"),
                ],
            )
        else:
            pkg_type = "typst"

    is_typst = pkg_type in ("typst", "typ")
    bundles = TYPST_PACKAGE_BUNDLES if is_typst else LATEX_PACKAGE_BUNDLES
    dest_file = target_dir / ("packages.typ" if is_typst else "packages.tex")

    options = [(b["id"], b["label"], b["desc"]) for b in bundles]
    preselected = [b["id"] for b in bundles if b.get("default", False)]

    if sys.stdin.isatty():
        fmt_name = "Typst" if is_typst else "LaTeX"
        chosen_ids = ui.multiselect(
            f"Select {fmt_name} packages to include in {dest_file.name}:",
            options,
            preselected=preselected,
        )
        if not chosen_ids:
            ui.warn("No packages selected. Using default recommended bundle.")
            chosen_ids = preselected
    else:
        chosen_ids = preselected

    content = generate_packages_manifest(pkg_type, chosen_ids)

    # Overwrite check if file exists
    if dest_file.exists() and sys.stdin.isatty():
        ans = (
            input(
                f"{ui.badge()} {ui.yellow(f'⚠️  {dest_file.name} already exists. Overwrite? [y/N]: ')}"
            )
            .strip()
            .lower()
        )
        if ans not in ("y", "yes"):
            ui.warn(f"Skipped {dest_file.name} (preserved existing file)")
            return dest_file

    dest_file.write_text(content, encoding="utf-8")
    ui.success(
        f"Generated dynamic package manifest ({len(chosen_ids)} bundles) at {dest_file}"
    )
    return dest_file


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

    import time
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
            is_tex = (meta.get("engine") == "latex") or target.startswith("latex") or target.startswith("tex")
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
                            allowed_files = ["packages.typ", f"{target_name}.typ", "library.bib"]

                for template_file in src_dir.glob("**/*"):
                    if template_file.is_file():
                        if (
                            "__pycache__" in template_file.parts
                            or template_file.suffix in (".pyc", ".pyo")
                        ):
                            continue

                        relative_path = template_file.relative_to(src_dir)
                        if (
                            allowed_files is not None
                            and str(relative_path) not in allowed_files
                        ):
                            continue

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
                                        ui.warn(f"Skipped {dest_path.name} (preserved existing file)")
                                        continue
                                except (KeyboardInterrupt, EOFError):
                                    print("\nAborted.")
                                    return scaffolded_any
                            else:
                                ui.warn(f"Skipped {dest_path.name} (file already exists; use -f/--force to overwrite)")
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
                                if dest_path.suffix == ".tex" and isinstance(val, str) and not mk.startswith("packages_"):
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
                            "__ENGINE__", metadata.get("engine", "typst") if metadata else "typst"
                        )
                        content = content.replace("__DATE__", date_fb)
                        dest_path.write_text(content, encoding="utf-8")
                        scaffolded_any = True
                        created_files.append(str(dest_path.relative_to(target_dir)))

            if found_in_dir:
                break

    if scaffolded_any and not dry_run:
        target_labels = [
            f"{r}:{targets_map[r]}"
            for r in resolved_roles
            if targets_map.get(r)
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


def run_interactive_mode(
    roles_db: dict[str, Role],
    aliases: dict[str, str],
    current_dir: Path,
    project_root: Path,
) -> tuple[str, list[str], dict[str, str]]:
    """Interactive role and command selector using arrow/spacebar menus."""
    is_subfolder = (project_root != current_dir) and (
        project_root / "flake.nix"
    ).exists()
    has_root_flake = (project_root / "flake.nix").exists()

    if is_subfolder:
        try:
            rel = current_dir.relative_to(project_root)
        except ValueError:
            rel = current_dir.name
        ui.info(f"Existing workspace detected at {ui.bold(str(project_root))}")
        cmd_options = [
            ("new", f"Add starter file in ./{rel}/", "Starter file in current directory"),
            ("shell", "Add flake.nix and .envrc", "DevShell at project root"),
            ("project", "Add project configs", "Root configs (pyproject.toml, etc.)"),
            ("init", "Create full setup", "Full workspace setup at project root"),
        ]
    elif has_root_flake:
        ui.info(f"Active workspace detected at {ui.bold(str(project_root))}")
        cmd_options = [
            ("new", "Add starter file", "Starter file in current directory"),
            ("shell", "Add flake.nix and .envrc", "DevShell at root"),
            ("project", "Add project configs", "Root configs (pyproject.toml, etc.)"),
            ("init", "Create full setup", "Full workspace setup (flake, envrc, configs, starter)"),
        ]
    else:
        cmd_options = [
            ("init", "Create full setup", "Flake, envrc, project configs, starter"),
            ("shell", "Add flake.nix and .envrc", "DevShell environment only"),
            ("project", "Add project configs", "Root configs (pyproject.toml, etc.)"),
            ("new", "Add starter file", "Starter file in current directory"),
        ]

    chosen_cmd = ui.select("Action:", cmd_options)

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
                chosen_target = ui.select(
                    f"Select template for {r}:", options
                )
                role_targets[r] = chosen_target

    return chosen_cmd, chosen_roles, role_targets


def handle_color_args():
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--no-color":
            ui.set_color_mode("never")
        elif arg.startswith("--color="):
            ui.set_color_mode(arg.split("=", 1)[1])
        elif arg == "--color" and i + 1 < len(sys.argv[1:]):
            ui.set_color_mode(sys.argv[1:][i + 1])


def main() -> None:
    handle_color_args()

    # Basic flags
    if any(a in ("--help", "-h", "help") for a in sys.argv[1:]):
        print_help()
        sys.exit(0)

    if any(a in ("-V", "--version", "-v", "version") for a in sys.argv[1:]):
        print(f"{ui.badge()} {ui.bold(f'v{__version__}')}")
        sys.exit(0)

    # Smart Paths & Asset Discovery
    pkg_root = Path(__file__).resolve().parent
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

    # Parse arguments
    args = sys.argv[1:]

    # Handle 'flaker list'
    if args and args[0] in ("list", "ls"):
        display_roles_list(roles_db, aliases)
        sys.exit(0)

    # Handle 'flaker info <role>'
    if args and args[0] in ("info", "show"):
        if len(args) < 2:
            ui.error("Missing role name for 'flaker info'. Example: flaker info python")
            sys.exit(1)
        display_role_info(args[1], roles_db, aliases, all_asset_dirs)
        sys.exit(0)

    # Flags extraction
    force = False
    dry_run = False
    auto_git = True
    no_direnv = False
    channel = None
    target_flag: str | None = None
    doc_title: str | None = None
    doc_author: str | None = None
    doc_theme: str | None = None
    doc_engine: str | None = None
    configure_packages_flag = False
    no_packages_flag = False

    filtered_args: list[str] = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-f", "--force"):
            force = True
        elif arg in ("-n", "--dry-run"):
            dry_run = True
        elif arg == "--no-git":
            auto_git = False
        elif arg == "--no-direnv":
            no_direnv = True
        elif arg in ("-p", "--packages", "--pkg"):
            configure_packages_flag = True
        elif arg in ("--no-packages", "--no-pkg"):
            no_packages_flag = True
        elif arg in ("--color", "--no-color") or arg.startswith("--color="):
            if arg == "--color" and i + 1 < len(args):
                i += 1
        elif arg in ("-c", "--channel"):
            if i + 1 < len(args):
                channel = args[i + 1]
                i += 1
            else:
                ui.error("--channel requires a channel name or url.")
                sys.exit(1)
        elif arg.startswith("--channel="):
            channel = arg.split("=", 1)[1]
        elif arg in ("-m", "--mode", "-t", "--target", "--type"):
            if i + 1 < len(args):
                target_flag = args[i + 1]
                i += 1
            else:
                ui.error(f"{arg} requires a target name (e.g. report, slides, paper).")
                sys.exit(1)
        elif arg.startswith(("--mode=", "--target=", "--type=")):
            target_flag = arg.split("=", 1)[1]
        elif arg in ("-e", "--engine"):
            if i + 1 < len(args):
                doc_engine = args[i + 1]
                i += 1
            else:
                ui.error(f"{arg} requires 'typst' or 'latex'.")
                sys.exit(1)
        elif arg.startswith("--engine="):
            doc_engine = arg.split("=", 1)[1]
        elif arg == "--title":
            if i + 1 < len(args):
                doc_title = args[i + 1]
                i += 1
            else:
                ui.error("--title requires a title string.")
                sys.exit(1)
        elif arg.startswith("--title="):
            doc_title = arg.split("=", 1)[1]
        elif arg == "--author":
            if i + 1 < len(args):
                doc_author = args[i + 1]
                i += 1
            else:
                ui.error("--author requires an author string.")
                sys.exit(1)
        elif arg.startswith("--author="):
            doc_author = arg.split("=", 1)[1]
        elif arg == "--theme":
            if i + 1 < len(args):
                doc_theme = args[i + 1]
                i += 1
            else:
                ui.error("--theme requires 'dark' or 'light'.")
                sys.exit(1)
        elif arg.startswith("--theme="):
            doc_theme = arg.split("=", 1)[1]
        elif arg in ("--help", "-h"):
            print_help()
            sys.exit(0)
        elif arg in ("-V", "--version", "-v"):
            print(f"{ui.badge()} {ui.bold(f'v{__version__}')}")
            sys.exit(0)
        else:
            filtered_args.append(arg)
        i += 1

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
    }

    command = ""
    resolved_roles: list[str] = []
    role_targets: dict[str, str] = {}

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
                    chosen_role = ui.select(
                        "Select role:", role_options
                    )
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

            # 1. Check if alias directly maps to role:target (e.g. "slides" -> "folio:slides", "md:report" -> "folio:report", "beamer" -> "folio:latex-slides")
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

            # 4. Check if item is a standalone target for any role (e.g. `flaker new slides` or `flaker new paper`)
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

        if target_flag:
            for r in resolved_roles:
                if r in roles_db and roles_db[r].targets:
                    resolved_t = resolve_role_target(r, target_flag, roles_db)
                    if not resolved_t:
                        valid_tgts = ", ".join(list(roles_db[r].targets.keys()))
                        ui.error(
                            f"Unknown target '{target_flag}' for role '{r}'. Available targets: {valid_tgts}"
                        )
                        sys.exit(1)
                    role_targets[r] = resolved_t

        for r in resolved_roles:
            if r in roles_db and roles_db[r].targets and r not in role_targets:
                if command == "shell":
                    continue
                if sys.stdin.isatty():
                    role_def = roles_db[r]
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
                    role_targets[r] = "report" if "report" in role_def.targets else list(role_def.targets.keys())[0]

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

    nixpkgs_url = resolve_nixpkgs_url(channel)

    configure_packages = False
    if "folio" in resolved_roles:
        if no_packages_flag:
            configure_packages = False
        elif configure_packages_flag:
            configure_packages = True

    # Prompt metadata interactively ONLY for the 'new' command (isolated starter document)
    interactive_meta = (command == "new")

    # Resolve metadata for Folio documents (title, author, theme, engine, packages)
    doc_metadata = resolve_document_metadata(
        project_name=project_name,
        resolved_roles=resolved_roles,
        role_targets=role_targets,
        title_flag=doc_title,
        author_flag=doc_author,
        theme_flag=doc_theme,
        engine_flag=doc_engine,
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
            force=force,
            dry_run=dry_run,
            auto_git=auto_git,
            no_direnv=no_direnv,
        )
        if not success:
            sys.exit(0)

    # 2. Project foundation scaffolding
    if command == "init":
        # Scaffold project root assets in root (current_dir)
        scaffold_assets(
            target_dir=current_dir,
            project_name=project_name,
            resolved_roles=resolved_roles,
            assets_dirs=all_asset_dirs,
            scope="project",
            force=force,
            dry_run=dry_run,
            auto_git=auto_git,
            project_root=current_dir,
            role_targets=role_targets,
            roles_db=roles_db,
            metadata=doc_metadata,
        )
        # Scaffold starter files in root (current_dir)
        scaffold_assets(
            target_dir=current_dir,
            project_name=project_name,
            resolved_roles=resolved_roles,
            assets_dirs=all_asset_dirs,
            scope="starter",
            force=force,
            dry_run=dry_run,
            auto_git=auto_git,
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
            force=force,
            dry_run=dry_run,
            auto_git=auto_git,
            project_root=project_root,
            role_targets=role_targets,
            roles_db=roles_db,
            metadata=doc_metadata,
        )

    elif command == "new":
        # Scaffold starter in current directory only
        scaffold_assets(
            target_dir=current_dir,
            project_name=project_name,
            resolved_roles=resolved_roles,
            assets_dirs=all_asset_dirs,
            scope="starter",
            force=force,
            dry_run=dry_run,
            auto_git=auto_git,
            project_root=project_root,
            role_targets=role_targets,
            roles_db=roles_db,
            metadata=doc_metadata,
        )


if __name__ == "__main__":
    main()
