# Basecamp ⛺⚡

> **Fast, Modular Nix Development Environments & Instant Project Scaffolding**

Basecamp is an opinionated, lightning-fast CLI utility that automates single-file Nix shell creation (`flake.nix`), sets up seamless `.envrc` direnv hooks, generates language-aware `.gitignore` files, and scaffolds modern starter templates for over 20 languages, frameworks, and cloud ecosystems.

---

## ✨ Features

- ⚡ **Instant DevShells**: Generates reproducible, multi-platform `flake.nix` and `.envrc` configurations in milliseconds.
- 🗂️ **Zero-Config Scaffolding**: Provides turnkey starter templates across 20+ language ecosystems with modern project structures (`main.py`, `Cargo.toml`, `build.zig`, `CMakeLists.txt`, `pom.xml`, etc.).
- 🛡️ **Overwrite Protection (`-f / --force`)**: Protects existing configurations from accidental overwrites with confirmation prompts.
- 🌿 **Automatic Git Staging**: Detects Git repositories and automatically stages generated files (`git add flake.nix .envrc .gitignore`) so Nix Flakes recognize them immediately.
- 🚫 **Smart `.gitignore` Generation**: Appends standard Nix/direnv ignores (`.direnv/`, `result`) and role-specific cache/build directories (`.venv/`, `target/`, `node_modules/`, `zig-cache/`, `_build/`, etc.).
- 🌐 **Configurable Nixpkgs Channels (`-c / --channel`)**: Easily switch between `nixos-26.05`, `unstable`, `24.11`, or custom flake URIs on the fly.
- 🔍 **Discovery & Inspection (`list` & `info`)**: Browse all available roles, categories, and aliases, or inspect exact packages, LSPs, and shell hooks before scaffolding.
- 🧭 **Interactive Stack Selector (`interactive`)**: Run `basecamp` with no arguments in any terminal for a clean interactive menu to choose stacks and commands.
- 🧩 **Extensible User Roles (`~/.config/basecamp/roles.toml`)**: Define custom organization or project roles without modifying Basecamp's code.
- 🔗 **Native Runtime Library Injection**: Automatically injects standard C runtime libraries (`stdenv.cc.cc.lib`, `zlib`, `glib`, `libxml2`, `openssl`, `libffi`) into `LD_LIBRARY_PATH`.
- 🦀 **Rust-Overlay Integration**: Seamlessly pulls and activates the `oxalica/rust-overlay` toolchain with `rust-analyzer` when Rust roles are selected.
- 🪶 **Pure & Ultra-Lightweight**: Zero external Python dependencies; 100% standard library core with sub-30ms startup.

---

## 🚀 Quick Start

Run Basecamp directly via Nix without installing:

```bash
# Interactive mode (launches terminal stack selector)
nix run github:SpanishSyntax/Basecamp

# Initialize a Python environment with uv, ruff, and ty LSP + project template
nix run github:SpanishSyntax/Basecamp -- init python

# Initialize a Zig project with zls and build.zig
nix run github:SpanishSyntax/Basecamp -- init zig

# Initialize a Folio workspace for clean Markdown report
basecamp init folio report

# Initialize a Folio workspace specifically for 16:9 slides presentation
basecamp init folio slides

# Initialize a Folio workspace for an academic IEEE paper
basecamp init folio paper

# Initialize native Typst or LaTeX workspaces directly
basecamp init typ                        # Native Typst workspace (report.typ + packages.typ)
basecamp init tex                        # Native LaTeX workspace (report.tex + packages.tex)
basecamp init typ:paper                  # Native Typst IEEE 2-column paper (paper.typ)
basecamp init tex:slides                 # Native LaTeX 16:9 Beamer slides (slides.tex)

# Drop starter documents directly using role shortcuts
basecamp new slides                      # 16:9 Markdown presentation (slides.md)
basecamp new paper                       # IEEE 2-column Markdown paper (paper.md)
basecamp new report                      # Clean Markdown report document (report.md)
basecamp new typ:paper                   # Native Typst paper (paper.typ)
basecamp new tex:slides                  # Native LaTeX Beamer slides (slides.tex)

# Drop a starter experiment file into current folder without touching root configs
basecamp new mv

# Generate only DevShell without starter files
basecamp shell rust next

# Scaffold project foundation files (packages.typ, report.typ, library.bib) to project root
basecamp project folio

# Combine roles: Rust backend + Next.js frontend + DevOps containers
nix run github:SpanishSyntax/Basecamp -- init rust next ops

# Target nixpkgs-unstable channel
nix run github:SpanishSyntax/Basecamp -- init go -c unstable

# Dry-run preview without writing files
nix run github:SpanishSyntax/Basecamp -- init rust --dry-run

# View all available roles and categories
nix run github:SpanishSyntax/Basecamp -- list
```

---

## 💻 CLI Commands & Options

```text
Usage: basecamp [options]
       basecamp <command> [roles...] [options]

Commands:
  init         Full workspace bootstrap (DevShell + project root files + starter).
  new          Drop starter files into current directory (e.g. main.py, plot.py).
  shell        Generate DevShell flake.nix, .envrc, and .gitignore at project root.
  project      Scaffold only project root foundation files (pyproject.toml, report.typ).
  packages     Interactively configure and dynamically generate package manifest.
  list         List all available roles, categories, and aliases.
  active       Diagnose and display active roles on current flake.
  info <role>  Display detailed information, packages, and starter files for a role.
  interactive  Launch interactive Bun-style role and command selector.

Options:
  -a, --active         Show only active roles on current flake.
  -m, --mode MODE      Document operating mode / scaffolding target (report, slides, paper, all).
  -t, --target TARGET  Alias for --mode.
  -e, --engine ENGINE  Compilation engine for Markdown ('typst' or 'latex').
  -p, --packages       Prompt to interactively configure packages dynamically.
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
```

---

## 🧰 Supported Roles & Ecosystems

| Ecosystem | Role | Aliases | Toolchain & LSP | Formatter / Linters |
| :--- | :--- | :--- | :--- | :--- |
| **Rust** | `rust` | `rs` | Oxalica Rust Stable + `rust-analyzer`, `lldb` | `cargo-fmt` |
| **Zig** | `zig` | - | Zig Compiler + `zls` (LSP) | Built-in `zig fmt` |
| **Python** | `python` | `py` | Python 3.14 + `uv`, `ty` | `ruff` (LSP + Formatter) |
| **Math & Visual** | `mathvis` | `mv` | Python 3.14 + `uv`, `ty` | `ruff` + Scientific Stack |
| **Go** | `go` | - | Go + `gopls`, `delve` | `goimports` (`gotools`), `golangci-lint` |
| **C** | `c` | - | GCC, GDB, CMake, Ninja, `clangd` | `clang-format` |
| **C++** | `cpp` | - | GCC, GDB, CMake, Ninja, `clangd` | `clang-format` |
| **Java** | `java` | - | OpenJDK 25, `jdtls`, Maven, Gradle | `google-java-format` |
| **.NET / C#** | `dotnet` | `cs`, `csharp` | .NET 9 SDK + Omnisharp | `dotnet format` |
| **Gleam** | `gleam` | - | Gleam + Erlang runtime + `rebar3` | `gleam format` |
| **Elixir** | `elixir` | `ex` | Elixir + Mix + `elixir-ls` | `mix format` |
| **Haskell** | `haskell` | `hs` | GHC + Cabal + `haskell-language-server` | `ormolu`, `hlint` |
| **Julia** | `julia` | - | Julia Bin (DifferentialEquations, Makie) | `julia-formatter` |
| **TypeScript / JS**| `ts` | `js` | Bun, `vtsls`, `typescript` | `prettierd` |
| **Svelte** | `svelte` | - | Bun, `svelte-language-server`, `vtsls` | `prettierd` |
| **Vue** | `vue` | - | Bun, `vue-language-server`, `vtsls` | `prettierd` |
| **Next.js** | `next` | `react` | Bun, `vtsls`, `typescript` | `prettierd` |
| **Folio (Markdown)** | `folio` / `md` | `md:report`, `md:slides`, `md:paper`, `report`, `slides`, `paper` | `pandoc`, `typst`, `tectonic`, `tinymist`, `texlab` | `typstyle` |
| **Folio (Typst)** | `typst` / `typ` | `typ:report`, `typ:slides`, `typ:paper`, `typst:report`, `typst:slides`, `typst:paper` | `typst`, `tinymist` (LSP) | `typstyle` |
| **Folio (LaTeX)** | `latex` / `tex` | `tex:report`, `tex:slides`, `tex:paper`, `latex:report`, `latex:slides`, `latex:paper`, `beamer` | `tectonic`, `texlab` (LSP) | - |
| **DevOps & Cloud** | `ops` | `devops`, `docker` | `docker-compose`, `lazydocker`, `kubectl`, `helm`, `k9s`, `dive` | - |

---

## 📝 Folio Document Engine (Standardized 3×3 Matrix)

Basecamp provides a symmetrical 9-way document scaffolding engine for [Folio](https://github.com/SpanishSyntax/Folio). Every document archetype is available across all three supported markup languages:

| Document Archetype | Markdown (`.md`) | Typst (`.typ`) | LaTeX (`.tex`) | Output / Layout Specification |
| :--- | :--- | :--- | :--- | :--- |
| **Technical Report** | `report.md` | `report.typ` | `report.tex` | Minimal sans-serif Inter layout (A4/Letter) |
| **16:9 Presentation** | `slides.md` | `slides.typ` | `slides.tex` | Apple Keynote-inspired widescreen slide deck |
| **Academic Paper** | `paper.md` | `paper.typ` | `paper.tex` | Dual-column IEEE Computer Society publication |

### Foundation Assets (`project/`)
When initializing a Folio workspace, Basecamp automatically scaffolds the corresponding shared foundation assets to the project root:
- `packages.typ`: Modular Typst preamble hub (`cetz`, `fletcher`, `physica`, `merman`, `tablex`, `algorithmic`, `codly`).
- `packages.tex`: Modular LaTeX preamble hub (`amsmath`, `mathtools`, `tikz`, `pgfplots`, `booktabs`, `tcolorbox`, `cleveref`).
- `library.bib`: Shared BibTeX bibliography database.
- `report.typ`, `slides.typ`, `paper.typ`: Re-usable Typst layout functions for Markdown conversion and native Typst authoring.

#### Interactive Package Configurator (`basecamp packages`)
You can dynamically assemble your package manifest at any time with sane defaults preselected:
```bash
basecamp packages typ                  # Interactively configure packages.typ via multi-select
basecamp packages tex                  # Interactively configure packages.tex via multi-select
basecamp init folio slides --packages  # Interactively choose package bundles during init
```

---

## 🧩 Custom User Roles (`~/.config/basecamp/roles.toml`)

You can define your own project roles and aliases without modifying Basecamp. Create `~/.config/basecamp/roles.toml`:

```toml
[roles.ocaml]
category = "Functional"
description = "OCaml compiler + dune + utop + ocaml-lsp"
pkgs = ["ocaml", "dune_3", "ocamlPackages.utop", "ocamlPackages.ocaml-lsp"]
hooks = ["printf '🐫 OCaml environment active\\n'"]
ignores = ["_build/"]

[aliases]
ml = "ocaml"
```

Basecamp will automatically merge your custom roles into `basecamp list`, `basecamp info`, and all scaffolding commands. You can also place custom starter templates inside `~/.config/basecamp/templates/<role_name>/`.

---

## 🛠️ Home Manager Configuration

Add Basecamp to your `flake.nix`:

```nix
{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    basecamp = {
      url = "github:SpanishSyntax/Basecamp";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, basecamp, ... }: {
    homeConfigurations.user = home-manager.lib.homeManagerConfiguration {
      modules = [
        basecamp.homeManagerModules.default
        {
          programs.basecamp.enable = true;
        }
      ];
    };
  };
}
```

Once enabled, `basecamp` is directly accessible in your interactive shell.

---

## 📁 Repository Structure

```text
Basecamp/
├── flake.nix               # Flake package & Home Manager module definition
├── pyproject.toml          # Standard PEP 517 / 621 Python project packaging
├── MANIFEST.in             # Manifest guaranteeing template asset bundling
├── LICENSE                 # MIT License
├── README.md               # Documentation & usage guide
└── src/
    └── basecamp/
        ├── __init__.py         # Package metadata
        ├── __main__.py         # python -m basecamp entrypoint
        ├── cli/                # Command handlers & CLI parser
        ├── core/               # Role models, registry, and environment generator
        ├── scaffold/           # Asset scaffolding, git staging, and manifests
        ├── ui/                 # Prism terminal UI facade
        ├── flake.template      # Base devShell template
        └── templates/          # Starter project templates for 20+ ecosystems
        ├── c/
        ├── cpp/
        ├── dotnet/
        ├── elixir/
        ├── folio/
        ├── gleam/
        ├── go/
        ├── haskell/
        ├── java/
        ├── julia/
        ├── mathvis/
        ├── ops/
        ├── python/
        ├── rust/
        ├── ts/
        └── zig/
```

---

## 📜 License

MIT © SpanishSyntax
