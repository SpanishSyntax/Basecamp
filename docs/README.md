<p align="center">
  <img src="assets/banner.png" alt="Expedition basecamp tents pitched on arctic ice" width="100%" />
</p>

# Basecamp ⛺

[Overview](README.md) • [Getting Started](getting-started.md) • [Architecture](architecture.md) • [CLI Reference](usage.md) • [Configuration](configuration.md)

---

> Modular Nix development environments, automatic direnv configuration, and multi-language project scaffolding.

Basecamp is a command-line tool designed to eliminate manual developer environment configuration. It generates reproducible, single-file Nix development shells (`flake.nix`), configures directory-based environment switching (`.envrc`), outputs language-specific `.gitignore` rules, and provisions starter project layouts across more than 20 programming language ecosystems.

---

## Why "Basecamp"? (The Lore)

> **basecamp** (`/ˈbeɪs.kæmp/`) — *noun:* The primary staging outpost pitched at the foot of a glacier, stocking provisions, shelters, and technical climbing gear before an expedition pushes into unmapped arctic ice.

In arctic exploration, mountaineers never traverse an icefield without first establishing an insulated staging ground. Equipment is checked, ropes are measured, and shelters are anchored before setting foot on moving terrain. Attempting to navigate modern software development without hermetic tooling presents an equivalent risk: divergent compiler versions, missing dynamic libraries, and unpinned global state undermine system reliability.

**Basecamp establishes a secure development outpost in seconds:**

- **Hermetic Staging**: Automatically generates single-file `flake.nix` development shells, wires `.envrc` direnv hooks, and writes language-aware `.gitignore` rules without global environment side effects.
- **Expedition Packs**: Supplies battle-tested configurations across 20+ programming languages and frameworks, handling language servers, formatters, and native C runtime dependencies uniformly.

---

## Architecture at a Glance

Basecamp is structured into decoupled components:

1. **Role Registry (`basecamp.core.registry`)**: Central index defining packages, language servers (LSP), formatters, shell hooks, and build cache ignore patterns for every supported ecosystem.
2. **Environment Generator (`basecamp.core.environment`)**: Synthesizes custom `flake.nix` and `.envrc` definitions by merging selected roles into an optimized, multi-system flake template.
3. **Scaffolding Engine (`basecamp.scaffold.engine`)**: Recursively copies and parameterizes project foundation and starter files, handling conflict detection, dry runs, and automatic Git staging.
4. **CLI Router (`basecamp.cli.router`)**: Handles command dispatch, target resolution (e.g. `snowpack:slides`, `python`), interactive terminal selection, and flag parsing.
5. **Terminal Interface (`basecamp.ui`)**: Terminal presentation layer powered by Prism, providing consistent typography, error reporting, and interactive prompts.

---

## Supported Ecosystems

Basecamp bundles complete toolchains, formatters, and language servers for over 20 programming languages and developer ecosystems:

| Ecosystem | Canonical Role | Aliases | Toolchain & Language Server | Linters & Formatters |
| :--- | :--- | :--- | :--- | :--- |
| **Rust** | `rust` | `rs` | Oxalica Rust Toolchain, `rust-analyzer`, `lldb` | `cargo-fmt` |
| **Python** | `python` | `py` | Python 3.14, `uv`, `ty` | `ruff` (LSP & Formatter) |
| **Zig** | `zig` | - | Zig Compiler, `zls` | Built-in `zig fmt` |
| **Go** | `go` | - | Go, `gopls`, `delve` | `goimports`, `golangci-lint` |
| **C / C++** | `c`, `cpp` | - | Clang / GCC, GDB, CMake, Ninja, `clangd` | `clang-format` |
| **TypeScript / JS** | `ts` | `js` | Bun, `vtsls`, TypeScript Compiler | `prettierd` |
| **Next.js / React** | `next` | `react` | Bun, `vtsls`, TypeScript, React tooling | `prettierd` |
| **Svelte / Vue** | `svelte`, `vue` | - | Bun, `svelte-language-server` / `vue-language-server` | `prettierd` |
| **Java** | `java` | - | OpenJDK 25, `jdtls`, Maven, Gradle | `google-java-format` |
| **.NET / C#** | `dotnet` | `cs`, `csharp` | .NET 9 SDK, Omnisharp | `dotnet format` |
| **Gleam** | `gleam` | - | Gleam, Erlang runtime, `rebar3` | `gleam format` |
| **Elixir** | `elixir` | `ex` | Elixir, Mix, `elixir-ls` | `mix format` |
| **Haskell** | `haskell` | `hs` | GHC, Cabal, `haskell-language-server` | `ormolu`, `hlint` |
| **Julia** | `julia` | - | Julia Bin (DifferentialEquations, Makie) | `julia-formatter` |
| **Scientific Plotting** | `barograph` | `bg`, `baro` | Python 3.14, `uv`, Barograph stack | `ruff` |
| **Snowpack** | `snowpack` | `typst`, `typ`, `slides`, `paper`, `report` | Typst, Pandoc, Tectonic, `tinymist`, `texlab` | `typstyle` |
| **DevOps / Containers** | `ops` | `devops`, `docker` | Docker Compose, Lazydocker, Kubectl, Helm, K9s | - |

---

## Documentation Navigation

- [Installation & Quick Start](getting-started.md): Installation methods and getting started in 60 seconds.
- [Architecture & Design Philosophy](architecture.md): Internal mechanisms, template rendering, safety checks, and library injection.
- [CLI Reference & Usage Guide](usage.md): Comprehensive reference of commands, subcommands, flags, and recipes.
- [Configuration & Advanced Options](configuration.md): Custom roles (`roles.toml`), direnv automation, and NixOS/Home Manager configuration.
