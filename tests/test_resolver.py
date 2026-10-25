from basecamp.cli import (
    BUILTIN_ALIASES,
    build_builtin_role_registry,
    find_role_for_standalone_target,
    resolve_nixpkgs_url,
    resolve_role_target,
)


def test_resolve_nixpkgs_url():
    assert resolve_nixpkgs_url(None) == "github:NixOS/nixpkgs/nixos-26.05"
    assert resolve_nixpkgs_url("26.05") == "github:NixOS/nixpkgs/nixos-26.05"
    assert resolve_nixpkgs_url("unstable") == "github:NixOS/nixpkgs/nixpkgs-unstable"
    assert resolve_nixpkgs_url("nixos-unstable") == "github:NixOS/nixpkgs/nixos-unstable"
    assert resolve_nixpkgs_url("24.11") == "github:NixOS/nixpkgs/nixos-24.11"
    assert (
        resolve_nixpkgs_url("github:custom/nixpkgs")
        == "github:custom/nixpkgs"
    )


def test_builtin_aliases():
    assert BUILTIN_ALIASES["py"] == "python"
    assert BUILTIN_ALIASES["rs"] == "rust"
    assert BUILTIN_ALIASES["mv"] == "mathvis"
    assert BUILTIN_ALIASES["md"] == "folio:paper"
    assert BUILTIN_ALIASES["slides"] == "folio:slides"
    assert BUILTIN_ALIASES["beamer"] == "folio:latex-slides"


def test_resolve_role_target():
    roles = build_builtin_role_registry("my_test_proj")
    assert resolve_role_target("folio", "report", roles) == "report"
    assert resolve_role_target("folio", "md-report", roles) == "report"
    assert resolve_role_target("folio", "slides", roles) == "slides"
    assert resolve_role_target("folio", "presentation", roles) == "slides"
    assert resolve_role_target("folio", "typst-paper", roles) == "typst-paper"
    assert resolve_role_target("folio", "typ", roles) == "typst-paper"
    assert resolve_role_target("folio", "latex-slides", roles) == "latex-slides"
    assert resolve_role_target("folio", "beamer", roles) == "latex-slides"
    assert resolve_role_target("folio", "nonexistent", roles) is None
    assert resolve_role_target("python", "any", roles) is None


def test_find_role_for_standalone_target():
    roles = build_builtin_role_registry("my_test_proj")
    match = find_role_for_standalone_target("slides", roles)
    assert match == ("folio", "slides")

    match = find_role_for_standalone_target("paper", roles)
    assert match == ("folio", "paper")

    match = find_role_for_standalone_target("typ-report", roles)
    assert match == ("folio", "typst-report")

    match = find_role_for_standalone_target("nonexistent", roles)
    assert match is None
