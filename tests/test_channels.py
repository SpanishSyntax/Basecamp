"""Dual-channel (stable + unstable) package sourcing."""

import tempfile
from pathlib import Path

from basecamp.cli import build_builtin_role_registry, prepare_flake_env
from basecamp.cli.commands.active import (
    detect_active_roles,
    detect_channels,
    extract_package_sets,
)
from basecamp.core.environment import collect_channel_packages
from basecamp.core.models import Role
from basecamp.core.registry import (
    STABLE_CHANNEL,
    resolve_nixpkgs_url,
    resolve_unstable_url,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = REPO_ROOT / "src" / "basecamp" / "flake.template"


def _render(roles: list[str], **kw) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        assert prepare_flake_env(
            project_root=tmp,
            resolved_roles=roles,
            roles_db=build_builtin_role_registry("t"),
            template_path=TEMPLATE_PATH,
            libs_list="zlib",
            nixpkgs_url=resolve_nixpkgs_url(None),
            force=True,
            auto_git=False,
            no_direnv=True,
            **kw,
        )
        return (tmp / "flake.nix").read_text()


def test_unstable_url_defaults():
    assert STABLE_CHANNEL == "nixos-26.05"
    assert resolve_unstable_url(None) == "github:NixOS/nixpkgs/nixpkgs-unstable"
    assert resolve_unstable_url("nixos-unstable") == (
        "github:NixOS/nixpkgs/nixos-unstable"
    )


def test_channel_pkgs_prefix_and_field():
    role = Role(pkgs=["a", "unstable.b"], hooks=[], unstable_pkgs=["c"])
    assert role.channel_pkgs() == (["a"], ["c", "b"])
    assert role.all_pkgs == ["a", "c", "b"]


def test_collect_dedup_unstable_wins_and_adhoc():
    db = {
        "x": Role(pkgs=["foo", "bar"], hooks=[]),
        "y": Role(pkgs=["foo"], hooks=[], unstable_pkgs=["bar"]),
    }
    stable, unstable = collect_channel_packages(["x", "y", "unstable.baz", "qux"], db)
    assert stable == ["foo", "qux"]
    assert unstable == ["bar", "baz"]


def test_generated_flake_has_two_inputs_and_split_lists():
    content = _render(["snowpack", "python"])
    assert 'nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";' in content
    assert 'nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixpkgs-unstable";' in content
    stable_raw, unstable_raw = extract_package_sets(content)
    assert set(unstable_raw.split()) == {"typst", "tinymist", "typstyle"}
    assert {"pandoc", "tectonic", "texlab", "python3"} <= set(stable_raw.split())
    assert "typst" not in stable_raw.split()


def test_custom_unstable_url_and_detection():
    content = _render(["snowpack"], unstable_url=resolve_unstable_url("nixos-unstable"))
    assert detect_channels(content) == ("nixos-26.05", "nixos-unstable")
    diags, extra, channel = detect_active_roles(
        content, build_builtin_role_registry("t"), {}
    )
    assert channel == "nixos-26.05"
    assert {d.role_key for d in diags} == {"snowpack"}
    assert extra == []


def test_extract_handles_nested_brackets_and_legacy():
    nested = """
        packages =
          (with pkgs; [(julia-bin.withPackages [ "A" "B" ]) gcc])
          ++ (with unstable; [typst]);
        buildInputs = libs;
    """
    s, u = extract_package_sets(nested)
    assert "gcc" in s and u.strip() == "typst"
    legacy = "packages = with pkgs; [python3 uv];\nlibs = with pkgs; [zlib];"
    s, u = extract_package_sets(legacy)
    assert s.split() == ["python3", "uv"] and u == ""


def test_unstable_extras_reported_with_prefix():
    content = _render(["python", "unstable.ripgrep"])
    _, extra, _ = detect_active_roles(content, build_builtin_role_registry("t"), {})
    assert "unstable.ripgrep" in extra
