"""Unit and CLI integration tests for 'basecamp active' and 'basecamp list --active'."""

import subprocess
import sys
import tempfile
from pathlib import Path

from basecamp.cli.commands.active import (
    detect_active_roles,
    diagnose_flake,
)
from basecamp.core.registry import build_builtin_role_registry

REPO_ROOT = Path(__file__).resolve().parent.parent


def run_basecamp(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Helper to run basecamp CLI in a subprocess with PYTHONPATH set."""
    import os

    env = dict(os.environ)
    existing_pp = os.environ.get("PYTHONPATH", "")
    src_dir = str(REPO_ROOT / "src")
    env["PYTHONPATH"] = f"{src_dir}:{existing_pp}" if existing_pp else src_dir
    cmd = [sys.executable, "-m", "basecamp", *args]
    return subprocess.run(
        cmd,
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def test_detect_active_roles_metadata_comment():
    roles_db = build_builtin_role_registry("test_proj")
    flake_content = """
# [basecamp] roles: python rust folio
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
  };
}
"""
    diags, extra, channel = detect_active_roles(flake_content, roles_db, {})
    detected_keys = [d.role_key for d in diags]
    assert "python" in detected_keys
    assert "rust" in detected_keys
    assert "folio" in detected_keys
    assert channel == "nixos-26.05"


def test_diagnose_flake_helper():
    roles_db = build_builtin_role_registry("test_proj")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        (tmp / "flake.nix").write_text("# [basecamp] roles: python\n{\n  inputs.nixpkgs.url = \"github:NixOS/nixpkgs/nixos-26.05\";\n}\n")
        (tmp / "pyproject.toml").write_text("[project]\nname = 'test'\n")

        diag = diagnose_flake(tmp, roles_db, {})
        assert len(diag.active_roles) == 1
        assert diag.active_roles[0].role_key == "python"
        assert "pyproject.toml" in diag.discovered_artifacts
        assert diag.channel == "nixos-26.05"


def test_detect_active_roles_from_shell_hooks():
    roles_db = build_builtin_role_registry("test_proj")
    # Legacy flake without explicit comment header
    flake_content = r"""
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
  };
  outputs = { ... }: {
    devShells.x86_64-linux.default = pkgs.mkShell {
      packages = with pkgs; [ uv python314 rust-bin ];
      shellHook = ''
        printf '\033[1;34m⛺  [basecamp]\033[0m 🐍 \033[1mPython\033[0m (uv + ruff) active\n'
        printf '\033[1;34m⛺  [basecamp]\033[0m 🦀 \033[1mRust\033[0m (stable) active\n'
      '';
    };
  };
}
"""
    diags, extra, channel = detect_active_roles(flake_content, roles_db, {})
    detected_keys = [d.role_key for d in diags]
    assert "python" in detected_keys
    assert "rust" in detected_keys


def test_detect_active_roles_from_option_c_badges():
    roles_db = build_builtin_role_registry("test_proj")
    # Option C formatted badges without header comment
    flake_content = r"""
{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
  outputs = { ... }: {
    devShells.x86_64-linux.default = pkgs.mkShell {
      packages = with pkgs; [];
      shellHook = ''
        printf '\033[1;34m⛺  [basecamp]\033[0m \033[1mWorkspace Initialized:\033[0m\n'
        printf ' \033[2m│\033[0m  \033[1;32m✓\033[0m 📝 \033[1mFolio\033[0m \033[2m(Polyglot)\033[0m\n'
        printf ' \033[2m│\033[0m  \033[1;32m✓\033[0m 📈 \033[1mBarograph\033[0m \033[2m(Scientific Stack)\033[0m\n'
      '';
    };
  };
}
"""
    diags, extra, channel = detect_active_roles(flake_content, roles_db, {})
    detected_keys = [d.role_key for d in diags]
    assert "folio" in detected_keys
    assert "barograph" in detected_keys


def test_detect_active_roles_from_package_signatures():
    roles_db = build_builtin_role_registry("test_proj")
    flake_content = """
{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  outputs = { ... }: {
    devShells.default = pkgs.mkShell {
      packages = with pkgs; [ typst typstyle my-custom-tool ];
    };
  };
}
"""
    diags, extra, channel = detect_active_roles(flake_content, roles_db, {})
    detected_keys = [d.role_key for d in diags]
    assert "folio" in detected_keys
    assert "my-custom-tool" in extra
    assert channel == "nixos-unstable"


def test_cli_active_no_flake():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        res = run_basecamp("active", cwd=tmp)
        assert res.returncode == 0
        assert "No flake.nix found" in res.stderr or "No flake.nix found" in res.stdout


def test_cli_active_single_role():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        # Bootstrap python environment
        init_res = run_basecamp("init", "py", "--no-direnv", "--no-git", cwd=tmp)
        assert init_res.returncode == 0

        # Run 'basecamp active'
        res = run_basecamp("active", cwd=tmp)
        assert res.returncode == 0
        assert "Active Roles Diagnostic" in res.stdout
        assert "python" in res.stdout
        assert "Python" in res.stdout

        # Run 'basecamp list --active'
        res_list_active = run_basecamp("list", "--active", cwd=tmp)
        assert res_list_active.returncode == 0
        assert "Active Roles Diagnostic" in res_list_active.stdout
        assert "python" in res_list_active.stdout

        # Run 'basecamp list -a'
        res_list_a = run_basecamp("list", "-a", cwd=tmp)
        assert res_list_a.returncode == 0
        assert "Active Roles Diagnostic" in res_list_a.stdout
        assert "python" in res_list_a.stdout

        # Run 'basecamp status'
        res_status = run_basecamp("status", cwd=tmp)
        assert res_status.returncode == 0
        assert "Active Roles Diagnostic" in res_status.stdout
        assert "python" in res_status.stdout


def test_cli_active_polyglot():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        # Bootstrap polyglot workspace
        init_res = run_basecamp("init", "py", "rust", "folio", "--no-direnv", "--no-git", cwd=tmp)
        assert init_res.returncode == 0

        res = run_basecamp("active", cwd=tmp)
        assert res.returncode == 0
        assert "Active Roles Diagnostic" in res.stdout
        assert "python" in res.stdout
        assert "rust" in res.stdout
        assert "folio" in res.stdout
        assert "role(s) configured" in res.stdout
