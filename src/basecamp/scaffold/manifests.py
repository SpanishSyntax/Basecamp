"""Typst and LaTeX package manifests and bundles for Basecamp."""

import sys
from pathlib import Path
from typing import Any, Sequence

from basecamp.ui import ui

TYPST_PACKAGE_BUNDLES: list[dict[str, Any]] = [
    {
        "id": "cetz",
        "label": "CeTZ (@preview/cetz:0.5.2)",
        "desc": "TikZ-like vector drawing canvas & scientific plotting engine",
        "default": True,
        "snippet": (
            "// --- 1. Vector Drawing & Graphing (The \"TikZ\" of Typst) ---\n"
            "// CeTZ provides a comprehensive TikZ-inspired vector canvas\n"
            '#import "@preview/cetz:0.5.2"\n'
        ),
    },
    {
        "id": "fletcher",
        "label": "Fletcher (@preview/fletcher:0.5.8)",
        "desc": "Commutative diagrams, finite state machines, and flowcharts",
        "default": True,
        "snippet": (
            "// Fletcher provides elegant commutative diagrams and state machines\n"
            '#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge\n'
        ),
    },
    {
        "id": "physica",
        "label": "Physica (@preview/physica:0.9.8)",
        "desc": "Advanced math, differential forms, matrices, and bra-kets",
        "default": True,
        "snippet": (
            "// --- 2. Advanced Mathematics & Physics Notation ---\n"
            "// Mathematica/Physics notation: differential forms, matrices, bra-kets\n"
            '#import "@preview/physica:0.9.8": *\n'
        ),
    },
    {
        "id": "mitex",
        "label": "MiTeX (@preview/mitex:0.2.7)",
        "desc": "Compile native LaTeX math equations directly inside Typst blocks",
        "default": False,
        "snippet": (
            "// MiTeX allows writing native LaTeX equations directly inside Typst blocks\n"
            '#import "@preview/mitex:0.2.7": mitex\n'
        ),
    },
    {
        "id": "merman",
        "label": "Merman (@preview/merman:0.1.0)",
        "desc": "Native Mermaid renderer for software flowcharts, sequences & ERDs",
        "default": True,
        "snippet": (
            "// --- 3. Flowcharts & Software Architecture Diagrams ---\n"
            "// Native Mermaid renderer for software flowcharts, sequences, and classes\n"
            '#import "@preview/merman:0.1.0": mermaid\n'
        ),
    },
    {
        "id": "tablex",
        "label": "Tablex (@preview/tablex:0.0.9)",
        "desc": "Publication-grade tables with custom colspans, rowspans & cell styling",
        "default": True,
        "snippet": (
            "// --- 4. Advanced Tables & Data Grids ---\n"
            "// Publication-grade table styling, custom colspans, rowspans, and cell styling\n"
            '#import "@preview/tablex:0.0.9": tablex, cellx, hlinex, vlinex\n'
        ),
    },
    {
        "id": "algorithmic",
        "label": "Algorithmic (@preview/algorithmic:1.0.7)",
        "desc": "Clean pseudocode typesetting with line numbering and indentation",
        "default": False,
        "snippet": (
            "// --- 5. Algorithmic Pseudocode ---\n"
            "// Clean pseudocode typesetting with line numbering and indentation\n"
            '#import "@preview/algorithmic:1.0.7": *\n'
        ),
    },
    {
        "id": "codly",
        "label": "Codly (@preview/codly:1.3.0)",
        "desc": "Enhanced source code blocks with line numbering and tab labels",
        "default": False,
        "snippet": (
            "// --- 6. Code Block Formatting (Codly) ---\n"
            "// Enhanced code blocks with line numbering, icons, and tab labels\n"
            '#import "@preview/codly:1.3.0": *\n'
        ),
    },
]

LATEX_PACKAGE_BUNDLES: list[dict[str, Any]] = [
    {
        "id": "typography",
        "label": "Typography & Fonts",
        "desc": "Fontspec, TeX Gyre Pagella, JetBrains Mono, Babel, Microtype",
        "default": True,
        "snippet": (
            "% --- 1. Core Typography, Fonts & Localization ---\n"
            "\\usepackage{fontspec}\n"
            "\\setmainfont{TeX Gyre Pagella}\n"
            "\\setmonofont{JetBrainsMono NFM}\n"
            "\\usepackage[english]{babel}\n"
            "\\usepackage{microtype}                  % Improved kerning and micro-typography\n"
            "\\providecommand{\\tightlist}{\\setlength{\\itemsep}{0pt}\\setlength{\\parskip}{0pt}}\n"
        ),
    },
    {
        "id": "math",
        "label": "Mathematics & Physics",
        "desc": "AMS-LaTeX, mathtools, bm, diffcoeff, siunitx",
        "default": True,
        "snippet": (
            "% --- 2. Mathematical Sciences & Physics ---\n"
            "\\usepackage{amsmath, amssymb, amsfonts} % Core AMS mathematical symbols & environments\n"
            "\\usepackage{mathtools}                  % Mathematical tools and extensions\n"
            "\\usepackage{bm}                         % Bold mathematical symbols (\\bm{\\alpha})\n"
            "\\usepackage{diffcoeff}                  % Clean derivative notation (\\diff{y}{x})\n"
            "\\usepackage{siunitx}                    % Comprehensive SI units formatting (\\qty{10}{\\meter\\per\\second})\n"
        ),
    },
    {
        "id": "tikz",
        "label": "TikZ & PGFPlots (Vector Graphics)",
        "desc": "TikZ, PGFPlots 1.18, arrows.meta, positioning, calc, tikz-cd",
        "default": True,
        "snippet": (
            "% --- 3. Vector Graphics, Plotting & Diagramming (TikZ) ---\n"
            "\\usepackage{graphicx}                   % Figure & image inclusion\n"
            "\\usepackage{xcolor}                     % Color model support\n"
            "\\usepackage{tikz}                       % TikZ vector drawing engine\n"
            "\\usetikzlibrary{\n"
            "  arrows.meta,                          % Modern arrow heads\n"
            "  positioning,                          % Relative node placement\n"
            "  calc,                                 % Coordinate calculations\n"
            "  shapes.geometric,                     % Advanced shapes\n"
            "  fit,                                  % Bounding box fitting\n"
            "  backgrounds                           % Background layers\n"
            "}\n"
            "\\usepackage{pgfplots}                   % High-quality scientific plotting\n"
            "\\pgfplotsset{compat=1.18}\n"
            "\\usepackage{tikz-cd}                    % Commutative & architecture flow diagrams\n"
        ),
    },
    {
        "id": "tables",
        "label": "Academic Tables & Structure",
        "desc": "Booktabs, tabularx, multirow, makecell, array, enumitem",
        "default": True,
        "snippet": (
            "% --- 4. Academic Tables & Structural Layout ---\n"
            "\\usepackage{booktabs}                   % Publication-quality horizontal rules\n"
            "\\usepackage{longtable}                  % Multi-page tables generated by Markdown/Pandoc\n"
            "\\usepackage{tabularx}                   % Tables with auto-expanding columns\n"
            "\\usepackage{multirow}                   % Multi-row table cells\n"
            "\\usepackage{makecell}                   % Flexible column headers & multi-line cells\n"
            "\\usepackage{array}                      % Extended array and tabular environments\n"
            "\\makeatletter\n"
            "\\@ifclassloaded{beamer}{}{\\usepackage{enumitem}}\n"
            "\\makeatother\n"
        ),
    },
    {
        "id": "boxes",
        "label": "Code Listings & Callouts",
        "desc": "Listings, tcolorbox with skins & breakable",
        "default": True,
        "snippet": (
            "% --- 5. Code Listings & Callout Containers ---\n"
            "\\usepackage{listings}                   % Source code syntax highlighting\n"
            "\\usepackage{tcolorbox}                  % Sleek modern callout frames & boxes\n"
            "\\tcbuselibrary{skins, breakable}\n"
        ),
    },
    {
        "id": "refs",
        "label": "Citations & Cross-Referencing",
        "desc": "Cite, ulem, hyperref, cleveref",
        "default": True,
        "snippet": (
            "% --- 6. Citations, Hyperlinks & Cross-Referencing ---\n"
            "\\usepackage{cite}                       % Standard numeric citation formatting\n"
            "\\usepackage[normalem]{ulem}             % Sophisticated underlining\n"
            "\\usepackage{hyperref}                   % Clickable hyper-links & PDF bookmarks\n"
            "\\hypersetup{\n"
            "  colorlinks=true,\n"
            "  linkcolor=blue!70!black,\n"
            "  citecolor=green!50!black,\n"
            "  urlcolor=blue!80!black\n"
            "}\n"
            "\\usepackage{cleveref}                   % Intelligent contextual references (\\cref{fig:model})\n"
        ),
    },
]


def generate_packages_manifest(
    pkg_type: str = "typst",
    selected_ids: Sequence[str] | None = None,
) -> str:
    """Generates a dynamic package manifest text for Typst or LaTeX."""
    is_typst = pkg_type in ("typst", "typ")
    bundles = TYPST_PACKAGE_BUNDLES if is_typst else LATEX_PACKAGE_BUNDLES

    if selected_ids is None:
        selected_set = {b["id"] for b in bundles if b.get("default", False)}
    else:
        selected_set = set(selected_ids)

    lines = []
    if is_typst:
        lines.append("// ========================================================")
        lines.append("// MODULAR TYPST PACKAGE MANIFEST (packages.typ)")
        lines.append("// Dynamically generated by Basecamp")
        lines.append("// ========================================================\n")
    else:
        lines.append("% ========================================================")
        lines.append("% MODULAR LATEX PACKAGE MANIFEST (packages.tex)")
        lines.append("% Dynamically generated by Basecamp")
        lines.append("% ========================================================\n")

    for bundle in bundles:
        if bundle["id"] in selected_set:
            lines.append(bundle["snippet"].strip())
            lines.append("")

    return "\n".join(lines).strip() + "\n"


def configure_packages_interactive(
    preferred_type: str | None = None,
    dest_dir: Path | None = None,
) -> Path | None:
    """
    Interactively configures and dynamically generates packages.typ or packages.tex
    using ui.multiselect with sane defaults preselected.
    """
    target_dir = dest_dir or Path.cwd()

    # Infer package type if not explicitly passed
    pkg_type = preferred_type
    if not pkg_type:
        has_typ = (target_dir / "packages.typ").exists() or list(
            target_dir.glob("*.typ")
        )
        has_tex = (target_dir / "packages.tex").exists() or list(
            target_dir.glob("*.tex")
        )
        if has_typ and not has_tex:
            pkg_type = "typst"
        elif has_tex and not has_typ:
            pkg_type = "latex"
        elif sys.stdin.isatty():
            pkg_type = ui.select(
                "Select package manifest to configure:",
                [
                    ("typst", "Typst package manifest (packages.typ)"),
                    ("latex", "LaTeX package manifest (packages.tex)"),
                ],
            )
        else:
            pkg_type = "typst"

    is_typst = pkg_type in ("typst", "typ")
    bundles = TYPST_PACKAGE_BUNDLES if is_typst else LATEX_PACKAGE_BUNDLES
    dest_file = target_dir / ("packages.typ" if is_typst else "packages.tex")

    options = [(b["id"], b["label"], b["desc"]) for b in bundles]
    preselected = [b["id"] for b in bundles if b.get("default", False)]

    if sys.stdin.isatty():
        fmt_name = "Typst" if is_typst else "LaTeX"
        chosen_ids = ui.multiselect(
            f"Select {fmt_name} packages to include in {dest_file.name}:",
            options,
            preselected=preselected,
        )
        if not chosen_ids:
            ui.warn("No packages selected. Using default recommended bundle.")
            chosen_ids = preselected
    else:
        chosen_ids = preselected

    content = generate_packages_manifest(pkg_type, chosen_ids)

    # Overwrite check if file exists
    if dest_file.exists() and sys.stdin.isatty():
        ans = (
            input(
                f"{ui.badge()} {ui.yellow(f'⚠️  {dest_file.name} already exists. Overwrite? [y/N]: ')}"
            )
            .strip()
            .lower()
        )
        if ans not in ("y", "yes"):
            ui.warn(f"Skipped {dest_file.name} (preserved existing file)")
            return dest_file

    dest_file.write_text(content, encoding="utf-8")
    ui.success(
        f"Generated dynamic package manifest ({len(chosen_ids)} bundles) at {dest_file}"
    )
    return dest_file
