from basecamp.cli import (
    BUILTIN_ALIASES,
    build_builtin_role_registry,
    find_role_for_standalone_target,
    resolve_nixpkgs_url,
    resolve_role_target,
)
from basecamp.core.models import Role


def test_resolve_nixpkgs_url():
    assert resolve_nixpkgs_url(None) == "github:NixOS/nixpkgs/nixos-26.05"
    assert resolve_nixpkgs_url("26.05") == "github:NixOS/nixpkgs/nixos-26.05"
    assert resolve_nixpkgs_url("unstable") == "github:NixOS/nixpkgs/nixpkgs-unstable"
    assert (
        resolve_nixpkgs_url("nixos-unstable") == "github:NixOS/nixpkgs/nixos-unstable"
    )
    assert resolve_nixpkgs_url("24.11") == "github:NixOS/nixpkgs/nixos-24.11"
    assert resolve_nixpkgs_url("github:custom/nixpkgs") == "github:custom/nixpkgs"


def test_builtin_aliases():
    assert BUILTIN_ALIASES["py"] == "python"
    assert BUILTIN_ALIASES["rs"] == "rust"
    assert BUILTIN_ALIASES["bg"] == "barograph"
    assert BUILTIN_ALIASES["baro"] == "barograph"
    assert BUILTIN_ALIASES["barograph"] == "barograph"
    assert BUILTIN_ALIASES["snow"] == "snowpack"
    assert BUILTIN_ALIASES["md"] == "snowpack"
    assert BUILTIN_ALIASES["slides"] == "snowpack"
    assert BUILTIN_ALIASES["beamer"] == "snowpack"


def test_resolve_role_target():
    roles = {
        "custom": Role(
            pkgs=[],
            hooks=[],
            targets={
                "report": {"aliases": ["doc", "md-report"]},
                "slides": {"aliases": ["presentation"]},
            },
        ),
        "python": Role(pkgs=[], hooks=[]),
    }
    assert resolve_role_target("custom", "report", roles) == "report"
    assert resolve_role_target("custom", "doc", roles) == "report"
    assert resolve_role_target("custom", "slides", roles) == "slides"
    assert resolve_role_target("custom", "presentation", roles) == "slides"
    assert resolve_role_target("custom", "nonexistent", roles) is None
    assert resolve_role_target("python", "any", roles) is None


def test_find_role_for_standalone_target():
    roles = {
        "custom": Role(
            pkgs=[],
            hooks=[],
            targets={
                "slides": {"aliases": ["presentation"]},
                "paper": {"aliases": ["article"]},
            },
        ),
    }
    match = find_role_for_standalone_target("slides", roles)
    assert match == ("custom", "slides")

    match = find_role_for_standalone_target("article", roles)
    assert match == ("custom", "paper")

    match = find_role_for_standalone_target("nonexistent", roles)
    assert match is None
