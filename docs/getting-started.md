# Getting Started with Basecamp

[Overview](README.md) • [Getting Started](getting-started.md) • [Architecture](architecture.md) • [CLI Reference](usage.md) • [Configuration](configuration.md)

---

## Installation

Basecamp is packaged for Nix, Home Manager, NixOS, and Python package managers.

### Running Directly via Nix (Recommended)

Basecamp can be executed without installing it globally on your system:

```bash
# Launch interactive mode
nix run github:SpanishSyntax/Basecamp

# Execute a specific command directly
nix run github:SpanishSyntax/Basecamp -- init python
```

### Home Manager

Add Basecamp to your `flake.nix` inputs and enable its Home Manager module:

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

### NixOS System Configuration

To install Basecamp system-wide across all user accounts:

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
    nixosConfigurations.hostname = nixpkgs.lib.nixosSystem {
      modules = [
        basecamp.nixosModules.default
        {
          programs.basecamp.enable = true;
        }
      ];
    };
  };
}
```

### Installing via Pip / Uv

You can also install Basecamp as a standard Python application:

```bash
# Using uv (fastest)
uv tool install git+https://github.com/SpanishSyntax/Basecamp.git

# Using standard pip
pip install git+https://github.com/SpanishSyntax/Basecamp.git
```

---

## Quick Start

### 1. Initialize a Python Project

Create a complete workspace with a pinned Nix shell (`flake.nix`), automatic environment activation (`.envrc`), `.gitignore`, project metadata (`pyproject.toml`), and a runnable `main.py`:

```bash
mkdir my-python-service && cd my-python-service
basecamp init python
```

If you use `direnv`, allow the directory once:

```bash
direnv allow
```

Your shell now has Python 3.14, `uv`, `ruff`, and `ty` loaded automatically.

### 2. Initialize a Systems Project (Zig or Rust)

To bootstrap a Zig project with `zls` and a standard `build.zig`:

```bash
mkdir my-zig-app && cd my-zig-app
basecamp init zig
```

For Rust with `rust-analyzer` and `cargo`:

```bash
mkdir my-rust-crate && cd my-rust-crate
basecamp init rust
```

### 3. Generate Only a DevShell

If you already have existing project files and only want to generate `flake.nix`, `.envrc`, and `.gitignore`:

```bash
basecamp shell go
```

### 4. Multi-Role Compositions

Combine multiple ecosystems into a single consolidated development environment:

```bash
# Rust backend + Next.js frontend + DevOps tools
basecamp init rust next ops
```

### 5. Dry-Run Inspection

Preview all generated files, packages, and hooks in your terminal without modifying disk state:

```bash
basecamp init python --dry-run
```
