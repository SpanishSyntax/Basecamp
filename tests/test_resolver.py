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
    assert BUILTIN_ALIASES["bg"] == "barograph"
    assert BUILTIN_ALIASES["baro"] == "barograph"
    assert BUILTIN_ALIASES["barograph"] == "barograph"
    assert BUILTIN_ALIASES["snow"] == "snowpack"
    assert BUILTIN_ALIASES["md"] == "snowpack:paper"
    assert BUILTIN_ALIASES["slides"] == "snowpack:slides"
    assert BUILTIN_ALIASES["beamer"] == "snowpack:latex-slides"


def test_resolve_role_target():
    roles = build_builtin_role_registry("my_test_proj")
    assert resolve_role_target("snowpack", "report", roles) == "report"
    assert resolve_role_target("snowpack", "md-report", roles) == "report"
    assert resolve_role_target("snowpack", "slides", roles) == "slides"
    assert resolve_role_target("snowpack", "presentation", roles) == "slides"
    assert resolve_role_target("snowpack", "typst-paper", roles) == "typst-paper"
    assert resolve_role_target("snowpack", "typ", roles) == "typst-paper"
    assert resolve_role_target("snowpack", "latex-slides", roles) == "latex-slides"
    assert resolve_role_target("snowpack", "beamer", roles) == "latex-slides"
    assert resolve_role_target("snowpack", "nonexistent", roles) is None
    assert resolve_role_target("python", "any", roles) is None


def test_find_role_for_standalone_target():
    roles = build_builtin_role_registry("my_test_proj")
    match = find_role_for_standalone_target("slides", roles)
    assert match == ("snowpack", "slides")

    match = find_role_for_standalone_target("paper", roles)
    assert match == ("snowpack", "paper")

    match = find_role_for_standalone_target("typ-report", roles)
    assert match == ("snowpack", "typst-report")

    match = find_role_for_standalone_target("nonexistent", roles)
    assert match is None
