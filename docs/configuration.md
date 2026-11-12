# Configuration & Advanced Options

[Overview](README.md) • [Getting Started](getting-started.md) • [Architecture](architecture.md) • [CLI Reference](usage.md) • [Configuration](configuration.md)

---

## Custom User Roles

Basecamp supports extending or overriding the built-in role registry via a user configuration file located at `~/.config/basecamp/roles.toml`.

### File Specification (`roles.toml`)

```toml
# Define a custom OCaml development environment
[roles.ocaml]
category = "Functional"
description = "OCaml compiler, dune build system, and ocaml-lsp"
pkgs = ["ocaml", "dune_3", "ocamlPackages.utop", "ocamlPackages.ocaml-lsp"]
hooks = ["printf 'OCaml development environment active\\n'"]
ignores = ["_build/", ".merlin"]

# Define an embedded robotics environment
[roles.embedded]
category = "Systems"
description = "ARM GCC toolchain, openocd, and serial monitor"
pkgs = ["gcc-arm-embedded", "openocd", "picocom", "gdb"]
hooks = ["export TARGET_ARCH=arm-none-eabi"]
ignores = ["build/"]

# Mix channels: `pkgs` come from stable (nixos-26.05), `unstable_pkgs` from nixpkgs-unstable.
# An `unstable.` prefix inside `pkgs` is equivalent (e.g. "unstable.helix").
[roles.notes]
category = "Typesetting"
description = "Typst notes with bleeding-edge compiler"
pkgs = ["pandoc"]
unstable_pkgs = ["typst", "tinymist"]

# Define custom aliases
[aliases]
ml = "ocaml"
arm = "embedded"
```

Once defined, these roles participate in all standard Basecamp commands:

```bash
basecamp list
basecamp info ocaml
basecamp init ocaml
```

### Custom Template Directories

You can supply custom starter templates for your roles by placing files in:

```
~/.config/basecamp/templates/<role_name>/
├── project/       # Scaffolding root files (copied during 'init' and 'project')
└── starter/       # Source code files (copied during 'init' and 'new')
```

---

## Direnv Integration

Basecamp coordinates automatically with `direnv` and `nix-direnv`:

1. When `basecamp init` or `basecamp shell` runs, it writes an `.envrc` containing:
   ```bash
   use flake
   ```
2. If `direnv` is available in your `$PATH`, Basecamp runs `direnv allow` automatically to authorize environment loading.
3. If you prefer to manage environment switching manually, supply `--no-direnv`:
   ```bash
   basecamp init python --no-direnv
   ```

---

## Environment Variables

Basecamp respects several environment variables for overrides in specialized deployment scenarios:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `FLAKE_TEMPLATE` | Path to a custom `flake.template` file. | Package internal `flake.template` |
| `BASECAMP_ASSETS` | Path to the directory containing role templates. | Package internal `templates/` |
| `LIBS_LIST` | Comma-separated list of runtime C libraries injected into `LD_LIBRARY_PATH`. | `stdenv.cc.cc.lib,zlib,glib,libxml2,openssl,libffi` |
| `NO_COLOR` | Standard UNIX variable to disable ANSI color formatting. | Unset |

---

## NixOS and Home Manager

### NixOS System Module

```nix
# flake.nix or configuration.nix
{
  programs.basecamp = {
    enable = true;
    package = inputs.basecamp.packages.${pkgs.system}.default;
  };
}
```

### Home Manager Module

The Home Manager module allows declarative management of Basecamp and custom `roles.toml` settings:

```nix
{
  programs.basecamp = {
    enable = true;
    settings = {
      roles = {
        solidity = {
          category = "Smart Contracts";
          description = "Solidity compiler and Foundry development framework";
          pkgs = ["foundry-bin" "solc"];
          hooks = ["printf 'Foundry environment ready\\n'"];
          ignores = ["cache/" "out/"];
        };
      };
      aliases = {
        eth = "solidity";
      };
    };
  };
}
```

When configured through Home Manager, `settings` are automatically serialized and placed at `~/.config/basecamp/roles.toml`.
