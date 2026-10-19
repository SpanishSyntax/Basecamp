from flaker.cli import generate_packages_manifest


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
