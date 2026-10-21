"""Built-in roles, aliases, and channel registries for Flaker."""

from flaker.core.models import Role


def fmt_status(icon: str, name: str, detail: str = "") -> str:
    """Formats shell status messages with ANSI colors and icons."""
    extra = f" ({detail})" if detail else ""
    return (
        f"printf '\\033[1;34m❄️  [flaker]\\033[0m {icon} "
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
                f"[ -f Cargo.toml ] || cargo init --name {folder_name} >/dev/null 2>&1 || {{ _flk_err=1; _flk_err_rust=1; }}",
                fmt_status("🦀", "Rust", "stable toolchain + rust-analyzer"),
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
                f"[ -f go.mod ] || go mod init {folder_name} >/dev/null 2>&1 || {{ _flk_err=1; _flk_err_go=1; }}",
                fmt_status("🐹", "Go", "Go toolchain + gopls"),
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
            hooks=[
                fmt_status("⚡", "Zig", "Zig toolchain + zls"),
            ],
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
                fmt_status("☕", "Java", "JDK 25 + jdtls"),
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
            icon="🐍",
            display_name="Python",
            status_detail="uv + ruff + ty",
            pkgs=[
                "python314",
                "uv",
                "ruff",
                "ty",
            ],
            hooks=[
                'export PYTHONPATH="$PWD\'\'${PYTHONPATH:+:$PYTHONPATH}"',
                "export UV_PYTHON_DOWNLOADS=never",
                "if [ -f pyproject.toml ]; then uv sync --quiet || { _flk_err=1; _flk_err_python=1; }; elif [ -f requirements.txt ] && [ ! -d .venv ]; then (uv venv --quiet && uv pip install -r requirements.txt --quiet) || { _flk_err=1; _flk_err_python=1; }; fi",
                "if [ -d .venv ]; then source .venv/bin/activate || { _flk_err=1; _flk_err_python=1; }; fi",
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
            icon="📐",
            display_name="Mathvis",
            status_detail="πthon 3.14 + Scientific Stack",
            pkgs=[
                "python314",
                "uv",
                "ruff",
                "ty",
            ],
            hooks=[
                'export PYTHONPATH="$PWD\'\'${PYTHONPATH:+:$PYTHONPATH}"',
                "export UV_PYTHON_DOWNLOADS=never",
                "if [ -f pyproject.toml ]; then uv sync --quiet || { _flk_err=1; _flk_err_mathvis=1; }; fi",
                "if [ -d .venv ]; then source .venv/bin/activate || { _flk_err=1; _flk_err_mathvis=1; }; fi",
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
            icon="🔵",
            display_name="Julia",
            status_detail="Julia S&C + Formatter",
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
            icon="🟦",
            display_name="JS/TS",
            status_detail="Bun + vtsls + prettierd",
            pkgs=["bun", "vtsls", "typescript", "prettierd"],
            hooks=[fmt_status("🟦", "JS/TS", "Bun + vtsls + prettierd")],
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
                "[ -f package.json ] || bun create svelte@latest . >/dev/null 2>&1 || { _flk_err=1; _flk_err_svelte=1; }",
                fmt_status("🟧", "Svelte 5", "Bun + svelte-ls"),
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
                "[ -f package.json ] || bun create vue@latest >/dev/null 2>&1 || { _flk_err=1; _flk_err_vue=1; }",
                fmt_status("🟢", "Vue", "Bun + vue-ls"),
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
                "[ -f package.json ] || bun create next-app >/dev/null 2>&1 || { _flk_err=1; _flk_err_next=1; }",
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
            icon="🌸",
            display_name="Gleam",
            status_detail="Gleam + Erlang runtime",
            pkgs=["gleam", "erlang", "rebar3"],
            hooks=[
                fmt_status("🌸", "Gleam", "Gleam + Erlang runtime"),
            ],
            ignores=["build/"],
        ),
        "elixir": Role(
            category="Functional",
            description="Elixir + Mix + elixir-ls",
            icon="💧",
            display_name="Elixir",
            status_detail="Elixir + Mix + elixir-ls",
            pkgs=["elixir", "elixir-ls"],
            hooks=[
                fmt_status("💧", "Elixir", "Elixir + Mix + elixir-ls"),
            ],
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
            icon="📝",
            display_name="Folio",
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
            hooks=[
                fmt_status("🐳", "DevOps", "Docker + K8s tooling"),
            ],
            ignores=[],
        ),
    }


BUILTIN_ALIASES: dict[str, str] = {
    "py": "python",
    "rs": "rust",
    "react": "next",
    "js": "ts",
    "mv": "mathvis",
    "md": "folio:paper",
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
