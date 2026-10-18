import os
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from flaker import __version__
from flaker.ui import ui


@dataclass
class Role:
    pkgs: list[str]
    hooks: list[str]
    category: str = "General"
    description: str = ""
    ignores: list[str] = field(default_factory=list)


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
                "nodePackages.svelte-language-server",
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
        # Document & Typesetting Workspaces
        # ------------------------------------------------------------
        "typst": Role(
            category="Typesetting",
            description="Typst + Tinymist LSP + typstyle",
            pkgs=[
                "typst",
                "tinymist",
                "typstyle",
            ],
            hooks=[
                'export TYPST_ROOT="$PWD"',
                fmt_status("📄", "Typst", "Tinymist LSP + typstyle"),
            ],
            ignores=[],
        ),
        "latex": Role(
            category="Typesetting",
            description="Tectonic + texlab + latexindent",
            pkgs=[
                "tectonic",
                "texlab",
                "texlivePackages.latexindent",
            ],
            hooks=[
                fmt_status("📜", "LaTeX", "Tectonic + texlab"),
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
        ),
        "folio": Role(
            category="Typesetting",
            description="Typst/Pandoc/LaTeX Markdown Document Engine",
            pkgs=[
                "typst",
                "pandoc",
                "tinymist",
                "typstyle",
                "tectonic",
            ],
            hooks=[
                fmt_status("📝", "Folio", "Typst/Pandoc/LaTeX Document Engine"),
            ],
            ignores=[],
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
    "typ": "typst",
    "tex": "latex",
    "hs": "haskell",
    "cs": "dotnet",
    "csharp": "dotnet",
    "devops": "ops",
    "docker": "ops",
    "ex": "elixir",
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
  init         Full workspace bootstrap (DevShell + project root files + starter).
  new          Drop starter files into current directory (e.g. main.py, plot.py).
  shell        Generate DevShell flake.nix, .envrc, and .gitignore at project root.
  project      Scaffold only project root foundation files (pyproject.toml, template.typ).
  list         List all available roles, categories, and aliases.
  info <role>  Display detailed information, packages, and starter files for a role.
  interactive  Launch interactive Bun-style role and command selector.

{ui.blue("Options:")}
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
  flaker new mv                          # Drop mathvis plot.py in current experiment folder
  flaker new typ                         # Drop typst main.typ in current folder
  flaker shell rust next                 # Setup DevShell without scaffolding files
  flaker project typst                   # Scaffold template.typ & library.bib to project root
  flaker list                            # View all registered language roles & aliases
""")


def display_roles_list(roles_db: dict[str, Role], aliases: dict[str, str]) -> None:
    """Prints a formatted terminal table of all registered roles."""
    reverse_aliases: dict[str, list[str]] = {}
    for alias, target in aliases.items():
        reverse_aliases.setdefault(target, []).append(alias)

    ui.header("FLAKER ROLES REGISTRY", width=96)
    role_hdr = ui.bold(f"{'ROLE':<12}")
    alias_hdr = ui.bold(f"{'ALIASES':<10}")
    cat_hdr = ui.bold(f"{'CATEGORY':<20}")
    desc_hdr = ui.bold("DESCRIPTION")
    print(f"{role_hdr} {alias_hdr} {cat_hdr} {desc_hdr}")
    print(ui.dim("-" * 96))

    # Group roles by category
    categories: dict[str, list[str]] = {}
    for r_key, role in roles_db.items():
        categories.setdefault(role.category, []).append(r_key)

    for cat in sorted(categories.keys()):
        for r_key in sorted(categories[cat]):
            role = roles_db[r_key]
            alias_str = ", ".join(reverse_aliases.get(r_key, []))
            r_col = ui.cyan(f"{r_key:<12}")
            a_col = ui.dim(f"{alias_str:<10}")
            print(f"{r_col} {a_col} {role.category:<20} {role.description}")

    print(ui.blue("=" * 96))
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
    resolved_name = aliases.get(role_name, role_name)
    if resolved_name not in roles_db:
        ui.error(
            f"Unknown role '{role_name}'. Run 'flaker list' to see available roles."
        )
        sys.exit(1)

    role = roles_db[resolved_name]
    rev_aliases = [a for a, t in aliases.items() if t == resolved_name]

    ui.header(f"Role Information: {resolved_name}", width=76)
    print(f"  {ui.bold('Category')}    : {role.category}")
    print(
        f"  {ui.bold('Aliases')}     : {', '.join(rev_aliases) if rev_aliases else ui.dim('none')}"
    )
    print(f"  {ui.bold('Summary')}     : {role.description}")
    print(f"\n  {ui.bold('Packages Included in DevShell:')}")
    for pkg in role.pkgs:
        print(f"    • {ui.cyan(pkg)}")

    print(f"\n  {ui.bold('Shell Activation Hooks:')}")
    for hook in role.hooks:
        print(f"    • {ui.dim(hook)}")

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


def scaffold_assets(
    target_dir: Path,
    project_name: str,
    resolved_roles: list[str],
    assets_dirs: list[Path],
    scope: str = "starter",
    dry_run: bool = False,
    auto_git: bool = True,
    project_root: Path | None = None,
) -> bool:
    """
    Copies role templates into the target directory based on scope:
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
                # Flat legacy directory
                subdirs_to_copy.append(role_assets_dir)

            for src_dir in subdirs_to_copy:
                for template_file in src_dir.glob("**/*"):
                    if template_file.is_file():
                        if (
                            "__pycache__" in template_file.parts
                            or template_file.suffix in (".pyc", ".pyo")
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

                        if not dest_path.exists():
                            dest_path.parent.mkdir(parents=True, exist_ok=True)
                            content = template_file.read_text(encoding="utf-8")
                            content = content.replace("__PROJECT_NAME__", project_name)
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


def run_interactive_mode(
    roles_db: dict[str, Role],
    aliases: dict[str, str],
    current_dir: Path,
    project_root: Path,
) -> tuple[str, list[str]]:
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
            (
                "new",
                f"Create starter file in ./{rel}/",
                "Drops starter script in current directory",
            ),
            (
                "shell",
                "Update DevShell environment at root",
                "flake.nix, .envrc, and .gitignore",
            ),
            (
                "project",
                "Scaffold project foundation files",
                "Scaffold root configs to workspace root",
            ),
            (
                "init",
                "Re-initialize workspace",
                "Full bootstrap (DevShell + project foundation + starter)",
            ),
        ]
    elif has_root_flake:
        ui.info(f"Active workspace detected at {ui.bold(str(project_root))}")
        cmd_options = [
            (
                "new",
                "Create a starter file in current directory",
                "Drop starter script (main.py, plot.py, etc.)",
            ),
            ("init", "Re-initialize workspace", "DevShell + root configs + starter"),
            (
                "shell",
                "DevShell environment only",
                "flake.nix, .envrc, and .gitignore at root",
            ),
            (
                "project",
                "Scaffold project foundation files",
                "Scaffold root configs to project root",
            ),
        ]
    else:
        cmd_options = [
            (
                "init",
                "Initialize full workspace",
                "DevShell flake.nix + project root configs + starter",
            ),
            (
                "shell",
                "DevShell environment only",
                "flake.nix, .envrc, and .gitignore at root",
            ),
            ("new", "Drop starter files into current directory", "Starter script only"),
            (
                "project",
                "Scaffold project foundation files",
                "Root configs only (pyproject.toml, template.typ)",
            ),
        ]

    chosen_cmd = ui.select("What would you like to do?", cmd_options)

    sorted_roles = sorted(roles_db.keys())
    role_options = [
        (r, f"{r:<10} [{roles_db[r].category}]", roles_db[r].description)
        for r in sorted_roles
    ]

    if chosen_cmd == "new":
        chosen_role = ui.select("Select role for starter file:", role_options)
        return chosen_cmd, [chosen_role]
    else:
        chosen_roles = ui.multiselect("Select roles for the stack:", role_options)
        if not chosen_roles:
            ui.warn("No roles selected. Exiting.")
            sys.exit(0)
        return chosen_cmd, chosen_roles


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
    }

    command = ""
    raw_roles: list[str] = []

    # Interactive trigger if no arguments provided in a TTY
    if not filtered_args:
        if sys.stdin.isatty():
            command, raw_roles = run_interactive_mode(
                roles_db, aliases, current_dir, project_root
            )
        else:
            print_help()
            sys.exit(1)
    elif filtered_args[0] == "interactive":
        command, raw_roles = run_interactive_mode(
            roles_db, aliases, current_dir, project_root
        )
    else:
        command = COMMAND_ALIASES.get(filtered_args[0], filtered_args[0])
        raw_roles = filtered_args[1:]

        # If subcommand given without roles in a TTY (e.g. 'flaker new' or 'flaker init')
        if command in ("init", "new", "shell", "project") and not raw_roles:
            if sys.stdin.isatty():
                sorted_roles = sorted(roles_db.keys())
                role_options = [
                    (r, f"{r:<10} [{roles_db[r].category}]", roles_db[r].description)
                    for r in sorted_roles
                ]
                if command == "new":
                    chosen_role = ui.select(
                        "Select role for starter file:", role_options
                    )
                    raw_roles = [chosen_role]
                else:
                    raw_roles = ui.multiselect(
                        f"Select roles for flaker {command}:", role_options
                    )
                    if not raw_roles:
                        ui.warn("No roles selected. Exiting.")
                        sys.exit(0)
            else:
                ui.error(
                    f"Missing roles for command '{command}'. Example: flaker {command} python"
                )
                sys.exit(1)

    # Enforce valid commands
    if command not in ("init", "new", "shell", "project"):
        ui.error(f"Unknown command '{command}'.\n")
        print_help()
        sys.exit(1)

    if not template_path.exists():
        ui.error(f"FLAKE_TEMPLATE path invalid or missing: {template_path}")
        sys.exit(1)

    nixpkgs_url = resolve_nixpkgs_url(channel)
    resolved_roles = [aliases.get(r.lower(), r.lower()) for r in raw_roles]

    # 1. DevShell generation (init and shell)
    if command in ("init", "shell"):
        success = prepare_flake_env(
            project_root=project_root,
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
        # Scaffold project root assets
        scaffold_assets(
            target_dir=project_root,
            project_name=project_name,
            resolved_roles=resolved_roles,
            assets_dirs=all_asset_dirs,
            scope="project",
            dry_run=dry_run,
            auto_git=auto_git,
            project_root=project_root,
        )
        # Scaffold starter files in current directory
        scaffold_assets(
            target_dir=current_dir,
            project_name=project_name,
            resolved_roles=resolved_roles,
            assets_dirs=all_asset_dirs,
            scope="starter",
            dry_run=dry_run,
            auto_git=auto_git,
            project_root=project_root,
        )

    elif command == "project":
        scaffold_assets(
            target_dir=project_root,
            project_name=project_name,
            resolved_roles=resolved_roles,
            assets_dirs=all_asset_dirs,
            scope="project",
            dry_run=dry_run,
            auto_git=auto_git,
            project_root=project_root,
        )

    elif command == "new":
        # Scaffold starter in current directory
        scaffold_assets(
            target_dir=current_dir,
            project_name=project_name,
            resolved_roles=resolved_roles,
            assets_dirs=all_asset_dirs,
            scope="starter",
            dry_run=dry_run,
            auto_git=auto_git,
            project_root=project_root,
        )
        # Ensure project foundation exists at project_root if running in a subdirectory
        if project_root != current_dir:
            scaffold_assets(
                target_dir=project_root,
                project_name=project_name,
                resolved_roles=resolved_roles,
                assets_dirs=all_asset_dirs,
                scope="project",
                dry_run=dry_run,
                auto_git=auto_git,
                project_root=project_root,
            )


if __name__ == "__main__":
    main()
