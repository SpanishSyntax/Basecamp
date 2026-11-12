# CLI Reference & Command Guide

[Overview](README.md) • [Getting Started](getting-started.md) • [Architecture](architecture.md) • [CLI Reference](usage.md) • [Configuration](configuration.md)

---

## Command Overview

Basecamp provides commands tailored to different stages of project initialization and environment management:

| Command | Aliases | Description |
| :--- | :--- | :--- |
| `basecamp init <roles...>` | - | Complete workspace bootstrap (DevShell + project root files + starter code). |
| `basecamp shell <roles...>` | `env`, `flake` | Scaffold only the DevShell (`flake.nix`, `.envrc`, `.gitignore`) at the project root. |
| `basecamp project <roles...>` | `base`, `root` | Scaffold project root foundation files (`pyproject.toml`, `Cargo.toml`, etc.). |
| `basecamp new <roles...>` | `starter`, `draft` | Drop starter source files into the current working directory (`main.py`, `main.rs`). |
| `basecamp list` | `ls` | List all available roles, categories, and aliases. |
| `basecamp active` | `status` | Display active roles detected on the current project's `flake.nix`. |
| `basecamp info <role>` | `show` | Display package manifests, LSPs, formatters, and starter assets for a role. |
| `basecamp interactive` | - | Launch the interactive terminal selector. |
| `basecamp mcp` | - | Start the Model Context Protocol (MCP) server over standard input/output. |

---

## Command Details

### `basecamp init`

Bootstraps a complete workspace from scratch. It executes DevShell synthesis, writes project root foundation files, and drops starter source code.

```bash
# Initialize a single role
basecamp init python

# Initialize a composite environment
basecamp init rust next ops

# Force overwrite of existing files
basecamp init zig --force

# Preview all generated files without writing to disk
basecamp init go --dry-run

# Pull an ad-hoc package from the unstable input
basecamp init python unstable.ruff
```

### `basecamp shell`

Generates only `flake.nix`, `.envrc`, and `.gitignore` at the project root. Does not write starter templates or application source files.

```bash
# Add a Rust DevShell to an existing repository
basecamp shell rust

# Add a multi-role shell without altering existing sources
basecamp shell go ops
```

### `basecamp new`

Drops starter files into the current directory. This is useful when you already have a shell set up and want sample code or additional module templates.

```bash
# Drop a Python starter file (main.py)
basecamp new python

# Drop a Barograph plotting template (plot.py)
basecamp new barograph
```

### `basecamp project`

Scaffolds only foundational project configuration files (e.g., package manifests, build scripts) at the project root without touching source code.

```bash
basecamp project python
```

---

## Discovery Commands

### `basecamp list`

Displays all built-in and user-defined roles categorized by domain, along with supported aliases.

```bash
basecamp list
```

To view only currently active roles in the current directory:

```bash
basecamp list --active
```

### `basecamp info`

Inspects a role in detail, showing exact Nix packages, formatters, language servers, activation shell hooks, ignore rules, and starter templates.

```bash
basecamp info rust
basecamp info python
basecamp info snowpack
```

---

## Interactive Mode

Running `basecamp` without arguments in an interactive terminal launches a guided terminal interface:

```bash
basecamp
# or explicitly:
basecamp interactive
```

From this menu, you can interactively select commands, browse roles categorized by ecosystem, toggle target templates, and review actions before execution.

---

## Command-Line Options & Flags

| Flag | Long Option | Description | Default |
| :--- | :--- | :--- | :--- |
| `-f` | `--force` | Overwrite existing files without interactive confirmation. | `false` |
| `-n` | `--dry-run` | Output generated file contents to stdout without writing to disk. | `false` |
| `-c` | `--channel` | Stable nixpkgs input: channel name or flake URL (`nixos-26.05`, `24.11`). | `nixos-26.05` |
| `-u` | `--unstable-channel` | Unstable nixpkgs input: channel name or flake URL (`nixpkgs-unstable`, `nixos-unstable`). | `nixpkgs-unstable` |
| `-a` | `--active` | Display only active roles detected on the current `flake.nix`. | `false` |
| `-m` | `--mode MODE` | Operating mode or template target (e.g. `slides`, `paper`, `report`). | Role default |
| `-t` | `--target TARGET` | Alias for `--mode`. | Role default |
| | `--no-direnv` | Skip creating `.envrc` and skip invoking `direnv allow`. | `false` |
| | `--no-git` | Skip automatic `git add` staging of generated files. | `false` |
| | `--color MODE` | Terminal color mode: `auto`, `always`, or `never`. | `auto` |
| | `--no-color` | Disable ANSI color formatting. | `false` |
| `-h` | `--help` | Show CLI help text and exit. | - |
| `-V` | `--version` | Show Basecamp version and exit. | - |

---

## Practical Recipes

### Recipe 1: Polyglot Full-Stack Application

Create a project with a Rust backend, Next.js frontend, and DevOps container utilities:

```bash
mkdir enterprise-app && cd enterprise-app
git init
basecamp init rust next ops
direnv allow
```

This single command provisions `cargo`, `rust-analyzer`, Bun, `vtsls`, Docker Compose, and Kubernetes tools in a single development shell.

### Recipe 2: Mixing Stable and Unstable Packages

Every generated flake has two inputs: `nixpkgs` (stable, `nixos-26.05`) and `nixpkgs-unstable`. Packages come from stable unless a role lists them under `unstable_pkgs` (the built-in Snowpack role does this for `typst`, `tinymist`, `typstyle`). Ad-hoc packages opt in with an `unstable.` prefix:

```bash
basecamp init snowpack                 # typst stack from unstable, pandoc/tectonic/texlab from stable
basecamp init python unstable.ruff     # ruff from unstable, rest stable
basecamp init python -c unstable       # point the *stable* input at unstable (everything bleeding-edge)
```

The generated `packages` attribute is split per source:

```nix
packages =
  (with pkgs; [pandoc tectonic texlab])
  ++ (with unstable; [typst tinymist typstyle]);
```

### Recipe 3: Headless Scaffolding in Automated Scripts

In CI pipelines or container initialization scripts where interactive prompts would hang:

```bash
basecamp init go --force --no-git --no-direnv
```
