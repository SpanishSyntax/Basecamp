"""CLI argument parsing, color flags, and usage help for Basecamp."""

import sys
from dataclasses import dataclass, field

from basecamp.ui import handle_color_args, ui

__all__ = [
    "ParsedArgs",
    "handle_color_args",
    "parse_cli_args",
    "print_help",
]


def print_help() -> None:
    """Prints the CLI usage instructions."""
    if ui.is_agent:
        print("""Basecamp - Polyglot Nix Flake DevShell & Scaffolding Engine
Usage: basecamp [command] [roles...] [options]

Commands:
  init [roles...]    Create reproducible workspace (flake.nix, .envrc, toolchain hooks)
  shell [roles...]   Generate flake.nix and .envrc only
  new <role>         Add starter file for supported roles (c, cpp, ops)
  project [roles...] Add project foundation configs (CMakeLists.txt, compose.yaml)
  list [--json]      List available roles and stacks
  active [--json]    Diagnose and display active roles on current flake
  info <role>        Display detailed information for a role
  mcp                Launch native MCP stdio server

Options:
  -A, --agent          Compact machine/agent friendly output mode
  --json               Structured JSON output mode
  --toon               Token-Oriented Object Notation (TOON) output mode
  -f, --force          Overwrite existing files without confirmation prompts
  -n, --dry-run        Preview generated files in stdout without writing
  -c, --channel NAME   Nixpkgs channel (default: nixos-26.05)
  --no-direnv          Skip generating .envrc and skip 'direnv allow'
  --no-git             Do not automatically stage generated files with 'git add'
  --color MODE         Color output mode: auto, always, never
  --no-color           Disable colored output
  -h, --help           Show this help message and exit
  -V, -v, --version    Show version and exit
""")
        return

    print(f"""{ui.badge()} {ui.bold("Polyglot Nix Flake DevShell & Scaffolding Engine")}

{ui.blue("Usage:")}
  basecamp [options]
  basecamp <command> [roles...] [options]

{ui.blue("Commands:")}
  init         Create workspace (flake.nix, .envrc, toolchain hooks).
  shell        Generate flake.nix and .envrc only.
  new          Add starter file for supported roles (c, cpp, ops).
  project      Add project configs (CMakeLists.txt, compose.yaml).
  list         List available roles and stacks.
  active       Diagnose and display active roles on current flake.
  info <role>  Display detailed information for a role.
  mcp          Start native Model Context Protocol (MCP) stdio server.
  interactive  Launch interactive stack and command selector.

{ui.blue("Options:")}
  -A, --agent          Compact agent-friendly output mode.
  --json               Structured JSON output mode.
  -a, --active         Show only active roles on current flake.
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
  basecamp                                 # Interactive stack selector
  basecamp init py                         # Setup Python DevShell (auto-runs uv init in shell)
  basecamp init rust next ops              # Polyglot workspace (Rust + Next.js + Docker)
  basecamp init snowpack                   # Setup Snowpack DevShell (Typst, Tinymist LSP, Tectonic)
  basecamp shell rust next                 # Setup DevShell without scaffolding files
  basecamp project c                       # Scaffold CMakeLists.txt to project root
  basecamp new c                           # Drop main.c in current directory
  basecamp list                            # View all registered language roles & aliases
  basecamp active                          # Diagnose active roles on current workspace flake
  basecamp list --active                   # Show active roles on current flake
""")


@dataclass
class ParsedArgs:
    """Normalized CLI arguments and options."""

    filtered_args: list[str] = field(default_factory=list)
    force: bool = False
    dry_run: bool = False
    auto_git: bool = True
    no_direnv: bool = False
    channel: str | None = None
    target_flag: str | None = None
    doc_title: str | None = None
    doc_author: str | None = None
    doc_theme: str | None = None
    doc_engine: str | None = None
    configure_packages_flag: bool = False
    no_packages_flag: bool = False
    active: bool = False


def parse_cli_args(args: list[str]) -> ParsedArgs:
    """Extracts flags and gathers positional arguments."""
    parsed = ParsedArgs()
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-f", "--force"):
            parsed.force = True
        elif arg in ("-n", "--dry-run"):
            parsed.dry_run = True
        elif arg in ("-a", "--active"):
            parsed.active = True
        elif arg in ("-A", "--agent", "--json", "--toon"):
            pass
        elif arg == "--no-git":
            parsed.auto_git = False
        elif arg == "--no-direnv":
            parsed.no_direnv = True
        elif arg in ("-p", "--packages", "--pkg"):
            parsed.configure_packages_flag = True
        elif arg in ("--no-packages", "--no-pkg"):
            parsed.no_packages_flag = True
        elif arg in ("--color", "--no-color") or arg.startswith("--color="):
            if arg == "--color" and i + 1 < len(args):
                i += 1
        elif arg in ("-c", "--channel"):
            if i + 1 < len(args):
                parsed.channel = args[i + 1]
                i += 1
            else:
                ui.error("--channel requires a channel name or url.")
                sys.exit(1)
        elif arg.startswith("--channel="):
            parsed.channel = arg.split("=", 1)[1]
        elif arg in ("-m", "--mode", "-t", "--target", "--type"):
            if i + 1 < len(args):
                parsed.target_flag = args[i + 1]
                i += 1
            else:
                ui.error(f"{arg} requires a target name (e.g. report, slides, paper).")
                sys.exit(1)
        elif arg.startswith(("--mode=", "--target=", "--type=")):
            parsed.target_flag = arg.split("=", 1)[1]
        elif arg in ("-e", "--engine"):
            if i + 1 < len(args):
                parsed.doc_engine = args[i + 1]
                i += 1
            else:
                ui.error(f"{arg} requires 'typst' or 'latex'.")
                sys.exit(1)
        elif arg.startswith("--engine="):
            parsed.doc_engine = arg.split("=", 1)[1]
        elif arg == "--title":
            if i + 1 < len(args):
                parsed.doc_title = args[i + 1]
                i += 1
            else:
                ui.error("--title requires a title string.")
                sys.exit(1)
        elif arg.startswith("--title="):
            parsed.doc_title = arg.split("=", 1)[1]
        elif arg == "--author":
            if i + 1 < len(args):
                parsed.doc_author = args[i + 1]
                i += 1
            else:
                ui.error("--author requires an author string.")
                sys.exit(1)
        elif arg.startswith("--author="):
            parsed.doc_author = arg.split("=", 1)[1]
        elif arg == "--theme":
            if i + 1 < len(args):
                parsed.doc_theme = args[i + 1]
                i += 1
            else:
                ui.error("--theme requires 'dark' or 'light'.")
                sys.exit(1)
        elif arg.startswith("--theme="):
            parsed.doc_theme = arg.split("=", 1)[1]
        else:
            parsed.filtered_args.append(arg)
        i += 1
    return parsed
