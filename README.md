<p align="center">
  <img src="assets/banner.png" alt="Expedition basecamp tents pitched on arctic ice" width="100%" />
</p>

# Basecamp ⛺

A command-line tool for single-file Nix development shells (`flake.nix`), automatic `.envrc` direnv configuration, and multi-language starter project scaffolding.

Basecamp generates reproducible, multi-platform development environments in milliseconds, wires direnv hooks, outputs language-aware `.gitignore` rules, and provisions complete starter templates across more than 20 programming language ecosystems.

---

> [!TIP]
> **Documentation Site**: Comprehensive guides, complete role specifications, and advanced configuration options are available on the **[Documentation Site](https://spanishsyntax.github.io/Basecamp)**.

---

## Why "Basecamp"? (The Lore)

> **basecamp** (`/ˈbeɪs.kæmp/`) — *noun:* The primary staging outpost pitched at the foot of a glacier, stocking provisions, shelters, and technical climbing gear before an expedition pushes into unmapped arctic ice.

In arctic exploration, mountaineers never traverse an icefield without first establishing an insulated staging ground. Equipment is checked, ropes are measured, and shelters are anchored before setting foot on moving terrain. Attempting to navigate modern software development without hermetic tooling presents an equivalent risk: divergent compiler versions, missing dynamic libraries, and unpinned global state undermine system reliability.

**Basecamp establishes a secure development outpost in seconds:**

- **Hermetic Staging**: Automatically scaffolds single-file `flake.nix` development shells, wires `.envrc` direnv hooks, and writes language-aware `.gitignore` rules without global environment side effects.
- **Expedition Packs**: Supplies battle-tested configurations across 20+ programming languages and frameworks, handling language servers, formatters, and native C runtime dependencies uniformly.

---

## Features

- **Reproducible DevShells**: Generates multi-platform `flake.nix` and `.envrc` configurations in milliseconds.
- **Turnkey Starter Scaffolding**: Provisions starter templates across 20+ language ecosystems with modern project structures (`main.py`, `Cargo.toml`, `build.zig`, `CMakeLists.txt`, `pom.xml`, etc.).
- **Overwrite Protection**: Safeguards existing project files with interactive confirmation prompts unless `-f` / `--force` is specified.
- **Automatic Git Staging**: Detects Git repositories and automatically stages generated files (`git add flake.nix .envrc .gitignore`) so Nix Flakes recognize them immediately.
- **Language-Aware Ignore Rules**: Generates targeted `.gitignore` files combining standard Nix ignores (`.direnv/`, `result`) with role-specific build and cache directories (`.venv/`, `target/`, `node_modules/`, `zig-cache/`).
- **Dual-Channel Flakes**: Every generated flake carries a pinned stable input (`nixos-26.05`) and a `nixpkgs-unstable` input. Roles choose per package via `pkgs` (stable) / `unstable_pkgs`; ad-hoc packages opt in with an `unstable.` prefix. Override either input with `-c` / `--channel` and `-u` / `--unstable-channel`.
- **Discovery and Inspection**: Interactively browse available roles via `basecamp list` or inspect package lists, language servers, and hooks with `basecamp info <role>`.
- **Interactive Terminal Selector**: Run `basecamp` without arguments in an interactive terminal to launch the menu-driven stack and command selector.
- **Extensible User Roles**: Define organization or project roles in `~/.config/basecamp/roles.toml` without modifying Basecamp sources.
- **C Runtime Library Injection**: Automatically injects standard C runtime libraries (`stdenv.cc.cc.lib`, `zlib`, `glib`, `libxml2`, `openssl`, `libffi`) into `LD_LIBRARY_PATH`.
- **Rust-Overlay Integration**: Seamlessly pulls and activates the `oxalica/rust-overlay` toolchain with `rust-analyzer` when Rust roles are selected.
- **Lightweight Architecture**: Pure standard library core with sub-30ms startup.

---

## Quick Start

Run Basecamp directly via Nix without installing:

```bash
# Interactive mode (launches terminal stack selector)
nix run github:SpanishSyntax/Basecamp

# Initialize a Python environment with uv, ruff, and ty LSP + project template
nix run github:SpanishSyntax/Basecamp -- init python

# Initialize a Zig project with zls and build.zig
nix run github:SpanishSyntax/Basecamp -- init zig

# Generate only DevShell without starter files
basecamp shell rust next

# Combine roles: Rust backend + Next.js frontend + DevOps containers
nix run github:SpanishSyntax/Basecamp -- init rust next ops

# Pull an extra ad-hoc package from nixpkgs-unstable
nix run github:SpanishSyntax/Basecamp -- init go unstable.golangci-lint

# Point the stable input at a different release
nix run github:SpanishSyntax/Basecamp -- init go -c 25.11

# Dry-run preview without writing files
nix run github:SpanishSyntax/Basecamp -- init rust --dry-run

# View all available roles and categories
nix run github:SpanishSyntax/Basecamp -- list
```

---

## CLI Reference

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
  interactive  Launch interactive role and command selector.

Options:
  -a, --active         Show only active roles on current flake.
  -m, --mode MODE      Document operating mode / scaffolding target (report, slides, paper, all).
  -t, --target TARGET  Alias for --mode.
  -e, --engine ENGINE  Compilation engine for Markdown ('typst' or 'latex').
  -p, --packages       Prompt to interactively configure packages dynamically.
  --title TITLE        Document title for Snowpack documents.
  --author AUTHOR      Document author for Snowpack documents.
  --theme THEME        Presentation theme for slides ('dark' or 'light').
  -f, --force          Overwrite existing files without confirmation prompts.
  -n, --dry-run        Preview generated files in stdout without writing.
  -c, --channel NAME   Stable nixpkgs input (default: nixos-26.05, e.g. 24.11).
  -u, --unstable-channel NAME
                       Unstable nixpkgs input (default: nixpkgs-unstable).
  --no-direnv          Skip generating .envrc and skip 'direnv allow'.
  --no-git             Do not automatically stage generated files with 'git add'.
  --color MODE         Color output mode: auto, always, never (default: auto).
  --no-color           Disable colored output.
  -h, --help           Show this help message and exit.
  -V, -v, --version    Show version and exit.
```

---

## Supported Roles & Ecosystems

| Ecosystem | Role | Aliases | Toolchain & LSP | Formatter / Linters |
| :--- | :--- | :--- | :--- | :--- |
| **Rust** | `rust` | `rs` | Oxalica Rust Stable + `rust-analyzer`, `lldb` | `cargo-fmt` |
| **Zig** | `zig` | - | Zig Compiler + `zls` (LSP) | Built-in `zig fmt` |
| **Python** | `python` | `py` | Python 3.14 + `uv`, `ty` | `ruff` (LSP + Formatter) |
| **Barograph / Plotting** | `barograph` | `bg`, `baro` | Python 3.14 + `uv`, `ty` | `ruff` + Barograph Scientific Stack |
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
| **Snowpack** | `snowpack` | `snow`, `typst`, `typ`, `tex`, `latex`, `md`, `slides`, `paper`, `report` | `pandoc`, `typst`, `tectonic`, `tinymist`, `texlab` | `typstyle` |
| **DevOps & Cloud** | `ops` | `devops`, `docker` | `docker-compose`, `lazydocker`, `kubectl`, `helm`, `k9s`, `dive` | - |

---

## Custom User Roles (`~/.config/basecamp/roles.toml`)

Define custom project roles and aliases without modifying Basecamp in `~/.config/basecamp/roles.toml`:

```toml
[roles.ocaml]
category = "Functional"
description = "OCaml compiler + dune + utop + ocaml-lsp"
pkgs = ["ocaml", "dune_3", "ocamlPackages.utop", "ocamlPackages.ocaml-lsp"]
hooks = ["printf 'OCaml environment active\\n'"]
ignores = ["_build/"]

[aliases]
ml = "ocaml"
```

Basecamp automatically merges user roles into `basecamp list`, `basecamp info`, and all scaffolding commands. Custom starter templates can be placed inside `~/.config/basecamp/templates/<role_name>/`.

---

## Home Manager Configuration

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

---

## License

MIT © SpanishSyntax
