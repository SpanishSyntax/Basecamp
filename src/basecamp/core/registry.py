"""Built-in roles, aliases, and channel registries for Basecamp."""

from basecamp.core.models import Role


def fmt_status(icon: str, name: str, detail: str = "") -> str:
    """Formats shell status messages with ANSI colors and icons."""
    extra = f" ({detail})" if detail else ""
    return (
        f"printf '\\033[1;34m⛺  [basecamp]\\033[0m {icon} "
        f"\\033[1m{name}\\033[0m{extra} active\\n'"
    )


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


def build_builtin_role_registry(folder_name: str) -> dict[str, Role]:
    """Constructs the dictionary of built-in language and tool stacks."""
    return {
        # ------------------------------------------------------------
        # Systems & Compiled Languages
        # ------------------------------------------------------------
        "rust": Role(
            category="Systems",
            description="Stable toolchain + rust-analyzer + lldb",
            icon="🦀",
            display_name="Rust",
            status_detail="stable toolchain + rust-analyzer",
            pkgs=[
                '(rust-bin.stable.latest.default.override { extensions = [ "rust-analyzer" ]; })',
                "cargo-expand",
                "lldb",
            ],
            hooks=[
                f"[ -f Cargo.toml ] || cargo init --name {folder_name}",
            ],
            ignores=["target/", "**/*.rs.bk"],
        ),
        "c": Role(
            category="Systems",
            description="GCC/Clang + clangd + cmake + ninja",
            icon="⚡",
            display_name="C",
            status_detail="GCC/Clang + clangd",
            pkgs=[
                "gcc",
                "gdb",
                "cmake",
                "pkg-config",
                "gnumake",
                "ninja",
                "clang-tools",
            ],
            hooks=[],
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
            icon="⚡",
            display_name="C++",
            status_detail="GCC/Clang + clangd",
            pkgs=[
                "gcc",
                "gdb",
                "cmake",
                "pkg-config",
                "gnumake",
                "ninja",
                "clang-tools",
            ],
            hooks=[],
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
            icon="🐹",
            display_name="Go",
            status_detail="Go toolchain + gopls",
            pkgs=[
                "go",
                "gopls",
                "gotools",
                "golangci-lint",
                "delve",
            ],
            hooks=[
                f"[ -f go.mod ] || go mod init {folder_name}",
            ],
            ignores=["bin/", "dist/"],
        ),
        "zig": Role(
            category="Systems",
            description="Zig compiler + zls LSP",
            icon="⚡",
            display_name="Zig",
            status_detail="Zig toolchain + zls",
            pkgs=[
                "zig",
                "zls",
            ],
            hooks=[],
            ignores=["zig-cache/", "zig-out/"],
        ),
        "java": Role(
            category="Systems",
            description="OpenJDK 25 + jdtls + maven/gradle",
            icon="☕",
            display_name="Java",
            status_detail="JDK 25 + jdtls",
            pkgs=[
                "jdk25",
                "jdt-language-server",
                "google-java-format",
                "maven",
                "gradle",
            ],
            hooks=[
                'export JAVA_HOME="${pkgs.jdk25}/lib/openjdk"',
            ],
            ignores=["target/", ".gradle/", "build/"],
        ),
        "dotnet": Role(
            category="Systems",
            description=".NET 9 SDK + Omnisharp",
            icon="🔷",
            display_name=".NET",
            status_detail=".NET 9 SDK + Omnisharp",
            pkgs=[
                "dotnet-sdk_9",
                "omnisharp-roslyn",
            ],
            hooks=[
                'export DOTNET_ROOT="${pkgs.dotnet-sdk_9}"',
            ],
            ignores=["bin/", "obj/"],
        ),
        # ------------------------------------------------------------
        # Scripting, Data & Scientific
        # ------------------------------------------------------------
        "python": Role(
            category="Data & Scientific",
            description="Python 3 + uv + ruff + ty",
            icon="🐍",
            display_name="Python",
            status_detail="uv + ruff + ty",
            pkgs=[
                "python3",
                "uv",
                "ruff",
                "ty",
            ],
            hooks=[
                'export PYTHONPATH="$PWD\'\'${PYTHONPATH:+:$PYTHONPATH}"',
                "export UV_PYTHON_DOWNLOADS=never",
                "if [ -f pyproject.toml ]; then uv sync --quiet; elif [ -f requirements.txt ] && [ ! -d .venv ]; then (uv venv --quiet && uv pip install -r requirements.txt --quiet); fi",
                "if [ -d .venv ]; then source .venv/bin/activate; fi",
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
        "barograph": Role(
            category="Data & Scientific",
            description="Barograph plot engine + Python scientific computation stack",
            icon="📈",
            display_name="Barograph",
            status_detail="Barograph Plot Engine + Scientific Stack",
            pkgs=[
                "python3",
                "uv",
                "ruff",
                "ty",
            ],
            hooks=[
                'export PYTHONPATH="$PWD\'\'${PYTHONPATH:+:$PYTHONPATH}"',
                "export UV_PYTHON_DOWNLOADS=never",
                "if [ -f pyproject.toml ]; then uv sync --quiet; fi",
                "if [ -d .venv ]; then source .venv/bin/activate; fi",
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
            icon="🔵",
            display_name="Julia",
            status_detail="Julia S&C + Formatter",
            pkgs=[
                '(julia-bin.withPackages [ "ControlSystems" "DifferentialEquations" "GLMakie" "CairoMakie" "LanguageServer" ])',
                "julia-formatter",
            ],
            hooks=[],
            ignores=[],
        ),
        # ------------------------------------------------------------
        # Web & Frontend Ecosystem
        # ------------------------------------------------------------
        "ts": Role(
            category="Web & Frontend",
            description="TypeScript/JS + Bun + vtsls + prettierd",
            icon="🟦",
            display_name="JS/TS",
            status_detail="Bun + vtsls + prettierd",
            pkgs=["bun", "vtsls", "typescript", "prettierd"],
            hooks=[],
            ignores=["node_modules/", "dist/"],
        ),
        "svelte": Role(
            category="Web & Frontend",
            description="Svelte 5 + Bun + svelte-ls",
            icon="🟧",
            display_name="Svelte 5",
            status_detail="Bun + svelte-ls",
            pkgs=[
                "bun",
                "svelte-language-server",
                "vtsls",
                "typescript",
                "prettierd",
            ],
            hooks=[
                "[ -f package.json ] || bun create svelte@latest .",
            ],
            ignores=["node_modules/", ".svelte-kit/", "build/"],
        ),
        "vue": Role(
            category="Web & Frontend",
            description="Vue + Bun + vue-ls",
            icon="🟢",
            display_name="Vue",
            status_detail="Bun + vue-ls",
            pkgs=[
                "bun",
                "vue-language-server",
                "vtsls",
                "typescript",
                "prettierd",
            ],
            hooks=[
                "[ -f package.json ] || bun create vue@latest",
            ],
            ignores=["node_modules/", "dist/"],
        ),
        "next": Role(
            category="Web & Frontend",
            description="Next.js + Bun + vtsls",
            icon="⚛️ ",
            display_name="Next.js",
            status_detail="Bun + vtsls",
            pkgs=[
                "bun",
                "vtsls",
                "typescript",
                "prettierd",
            ],
            hooks=[
                "[ -f package.json ] || bun create next-app",
            ],
            ignores=["node_modules/", ".next/", "out/"],
        ),
        # ------------------------------------------------------------
        # Functional Ecosystem
        # ------------------------------------------------------------
        "gleam": Role(
            category="Functional",
            description="Gleam + Erlang runtime + rebar3",
            icon="🌸",
            display_name="Gleam",
            status_detail="Gleam + Erlang runtime",
            pkgs=["gleam", "erlang", "rebar3"],
            hooks=[],
            ignores=["build/"],
        ),
        "elixir": Role(
            category="Functional",
            description="Elixir + Mix + elixir-ls",
            icon="💧",
            display_name="Elixir",
            status_detail="Elixir + Mix + elixir-ls",
            pkgs=["elixir", "elixir-ls"],
            hooks=[],
            ignores=["_build/", "deps/"],
        ),
        "haskell": Role(
            category="Functional",
            description="GHC + Cabal + HLS + Ormolu",
            icon="λ ",
            display_name="Haskell",
            status_detail="GHC + Cabal + HLS + Ormolu",
            pkgs=[
                "ghc",
                "cabal-install",
                "haskell-language-server",
                "hlint",
                "ormolu",
            ],
            hooks=[],
            ignores=["dist-newstyle/", ".cabal-sandbox/"],
        ),
        # ------------------------------------------------------------
        # Document & Typesetting Workspaces (Unified under Snowpack)
        # ------------------------------------------------------------
        "snowpack": Role(
            category="Typesetting",
            description="Polyglot Document Engine (Typst + LaTeX + Markdown)",
            icon="📝",
            display_name="Snowpack",
            status_detail="Polyglot Document Engine (Typst + LaTeX)",
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
                    "aliases": ["md-report", "doc", "document"],
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
                    "aliases": ["md-paper", "ieee", "article", "default"],
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
            icon="🐳",
            display_name="DevOps",
            status_detail="Docker + K8s tooling",
            pkgs=[
                "docker-compose",
                "lazydocker",
                "kubectl",
                "kubernetes-helm",
                "k9s",
                "dive",
            ],
            hooks=[],
            ignores=[],
        ),
    }


BUILTIN_ALIASES: dict[str, str] = {
    "py": "python",
    "rs": "rust",
    "react": "next",
    "js": "ts",
    "bg": "barograph",
    "baro": "barograph",
    "barograph": "barograph",
    "snow": "snowpack",
    "snowpack": "snowpack",
    "md": "snowpack:paper",
    "typ": "snowpack:typst-report",
    "typst": "snowpack:typst-report",
    "typst-paper": "snowpack:typst-paper",
    "typst-report": "snowpack:typst-report",
    "typst-slides": "snowpack:typst-slides",
    "typst:paper": "snowpack:typst-paper",
    "typst:report": "snowpack:typst-report",
    "typst:slides": "snowpack:typst-slides",
    "typ-paper": "snowpack:typst-paper",
    "typ-report": "snowpack:typst-report",
    "typ-slides": "snowpack:typst-slides",
    "typ:paper": "snowpack:typst-paper",
    "typ:report": "snowpack:typst-report",
    "typ:slides": "snowpack:typst-slides",
    "tex": "snowpack:latex-report",
    "latex": "snowpack:latex-report",
    "latex-paper": "snowpack:latex-paper",
    "latex-report": "snowpack:latex-report",
    "latex-slides": "snowpack:latex-slides",
    "latex:paper": "snowpack:latex-paper",
    "latex:report": "snowpack:latex-report",
    "latex:slides": "snowpack:latex-slides",
    "tex-report": "snowpack:latex-report",
    "tex-slides": "snowpack:latex-slides",
    "tex-paper": "snowpack:latex-paper",
    "tex:report": "snowpack:latex-report",
    "tex:slides": "snowpack:latex-slides",
    "tex:paper": "snowpack:latex-paper",
    "beamer": "snowpack:latex-slides",
    "hs": "haskell",
    "cs": "dotnet",
    "csharp": "dotnet",
    "devops": "ops",
    "docker": "ops",
    "ex": "elixir",
    "slides": "snowpack:slides",
    "presentation": "snowpack:slides",
    "paper": "snowpack:paper",
    "report": "snowpack:report",
    "md-report": "snowpack:report",
    "md-slides": "snowpack:slides",
    "md-paper": "snowpack:paper",
    "md:report": "snowpack:report",
    "md:slides": "snowpack:slides",
    "md:paper": "snowpack:paper",
}
