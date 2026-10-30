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
  init [roles...]    Create full setup (flake, envrc, project configs, starter)
  new <target>       Add starter file (main.py, report.md, etc.)
  shell [roles...]   Add flake.nix and .envrc
  project [roles...] Add project configs
  packages <role>    Configure package bundles
  list [--json]      List available roles and stacks
  active [--json]    Diagnose and display active roles on current flake
  info <role>        Display detailed information for a role

Options:
  -A, --agent          Compact machine/agent friendly output mode
  --json               Structured JSON output mode
  -m, --mode MODE      Document operating mode / target (report, slides, paper)
  -t, --target TARGET  Alias for --mode
  -e, --engine ENGINE  Compilation engine for Markdown ('typst' or 'latex')
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
  init         Create full setup (flake, envrc, project configs, starter).
  new          Add starter file (main.py, report.md, etc.).
  shell        Add flake.nix and .envrc.
  project      Add project configs (pyproject.toml, packages.typ, etc.).
  packages     Configure package bundles.
  list         List available roles and stacks.
  active       Diagnose and display active roles on current flake.
  info <role>  Display detailed information for a role.
  interactive  Launch interactive stack and command selector.

{ui.blue("Options:")}
  -A, --agent          Compact agent-friendly output mode.
  --json               Structured JSON output mode.
  -a, --active         Show only active roles on current flake.
  -m, --mode MODE      Document operating mode / target (report, slides, paper).
  -t, --target TARGET  Alias for --mode.
  -e, --engine ENGINE  Compilation engine for Markdown ('typst' or 'latex').
  -p, --packages       Configure packages dynamically (default in interactive mode).
  --no-pkg             Skip interactive package bundle selection.
  --no-packages        Alias for --no-pkg.
  --title TITLE        Document title for Snowpack documents.
  --author AUTHOR      Document author for Snowpack documents.
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

{ui.blue("Examples:")}
  basecamp                                 # Interactive Bun-style stack selector
  basecamp init py                         # Setup Python DevShell, root configs, and starter
  basecamp init py cpp rust typ            # Polyglot multi-language workspace bootstrap
  basecamp init snowpack report            # Setup Snowpack workspace for clean report document
  basecamp init snowpack slides            # Setup Snowpack workspace for 16:9 presentation slides
  basecamp init snowpack paper             # Setup Snowpack workspace for IEEE 2-column paper
  basecamp init snowpack slides --packages # Scaffold slides and interactively pick package bundles
  basecamp packages typ                    # Interactively configure Typst packages (packages.typ)
  basecamp packages tex                    # Interactively configure LaTeX packages (packages.tex)
  basecamp init typ                        # Setup native Typst workspace (report.typ + packages.typ)
  basecamp init tex                        # Setup native LaTeX workspace (report.tex + packages.tex)
  basecamp new md:slides                   # Drop slides.md in current folder
  basecamp new typ:paper                   # Drop native Typst IEEE 2-column paper (paper.typ)
  basecamp new tex:slides                  # Drop native LaTeX Beamer presentation (slides.tex)
  basecamp new paper                       # Direct shortcut to drop paper.md in current folder
  basecamp init snowpack -m slides         # Bootstrap slides using explicit --mode flag
  basecamp new bg                          # Drop Barograph starter (plot.py + dashboard.py) in current folder
  basecamp new typ                         # Drop native Typst report (report.typ) in current folder
  basecamp shell rust next                 # Setup DevShell without scaffolding files
  basecamp project snowpack                # Scaffold layout templates & library.bib to project root
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
        elif arg in ("-A", "--agent", "--json"):
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
