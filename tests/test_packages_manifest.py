from pathlib import Path
from basecamp.cli import generate_packages_manifest


def test_typst_starter_templates_root_import():
    templates_dir = Path(__file__).resolve().parent.parent / "src" / "basecamp" / "templates" / "snowpack" / "starter"
    typ_files = list(templates_dir.glob("*.typ"))
    assert len(typ_files) >= 3
    for typ_file in typ_files:
        content = typ_file.read_text(encoding="utf-8")
        assert '#import "/packages.typ": *' in content, f"{typ_file.name} must import '/packages.typ'"
        assert '#import "packages.typ": *' not in content, f"{typ_file.name} should not use relative import"
        assert 'bibliography("/library.bib"' in content, f"{typ_file.name} must reference '/library.bib'"
        assert 'bibliography("library.bib"' not in content, f"{typ_file.name} should not use relative bibliography path"



def test_generate_typst_packages_manifest_default():
    manifest = generate_packages_manifest("typst")
    assert "// MODULAR TYPST PACKAGE MANIFEST (packages.typ)" in manifest
    assert "@preview/cetz" in manifest
    assert "@preview/fletcher" in manifest
    assert "@preview/physica" in manifest
    assert "@preview/merman" in manifest
    assert "@preview/tablex" in manifest


def test_generate_typst_packages_manifest_custom():
    manifest = generate_packages_manifest("typst", selected_ids=["cetz", "codly"])
    assert "@preview/cetz" in manifest
    assert "@preview/codly" in manifest
    assert "@preview/physica" not in manifest


def test_generate_latex_packages_manifest_default():
    manifest = generate_packages_manifest("latex")
    assert "% MODULAR LATEX PACKAGE MANIFEST (packages.tex)" in manifest
    assert "fontspec" in manifest
    assert "amsmath" in manifest
    assert "tikz" in manifest
    assert "booktabs" in manifest
