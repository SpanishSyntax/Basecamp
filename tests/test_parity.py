"""Rigorous parity verification tests comparing against historical specifications."""

import subprocess
import sys
import tempfile
from pathlib import Path

from basecamp.cli.resolver import (
    find_role_for_standalone_target,
)
from basecamp.core.registry import (
    BUILTIN_ALIASES,
    build_builtin_role_registry,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = REPO_ROOT / "src" / "basecamp" / "flake.template"
ASSETS_DIR = REPO_ROOT / "src" / "basecamp" / "templates"


def run_basecamp(
    *args: str, cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
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


def test_builtin_registry_completeness():
    roles = build_builtin_role_registry("test_proj")
    expected_roles = {
        "rust",
        "c",
        "cpp",
        "go",
        "zig",
        "java",
        "dotnet",
        "python",
        "barograph",
        "julia",
        "ts",
        "svelte",
        "vue",
        "next",
        "gleam",
        "elixir",
        "haskell",
        "snowpack",
        "ops",
    }
    assert expected_roles.issubset(set(roles.keys()))

    # Verify Snowpack is a decoupled environment provider
    snowpack = roles["snowpack"]
    assert "typst" in snowpack.pkgs
    assert "tinymist" in snowpack.pkgs
    assert len(snowpack.targets) == 0


def test_alias_parity():
    # Verify canonical shortcuts
    assert BUILTIN_ALIASES["py"] == "python"
    assert BUILTIN_ALIASES["rs"] == "rust"
    assert BUILTIN_ALIASES["js"] == "ts"
    assert BUILTIN_ALIASES["bg"] == "barograph"
    assert BUILTIN_ALIASES["baro"] == "barograph"
    assert BUILTIN_ALIASES["barograph"] == "barograph"
    assert BUILTIN_ALIASES["snow"] == "snowpack"
    assert BUILTIN_ALIASES["md"] == "snowpack"
    assert BUILTIN_ALIASES["slides"] == "snowpack"
    assert BUILTIN_ALIASES["paper"] == "snowpack"
    assert BUILTIN_ALIASES["report"] == "snowpack"
    assert BUILTIN_ALIASES["typ"] == "snowpack"
    assert BUILTIN_ALIASES["tex"] == "snowpack"
    assert BUILTIN_ALIASES["beamer"] == "snowpack"


def test_cli_dry_run_parity():
    # basecamp init rust --dry-run
    res = run_basecamp("init", "rust", "--dry-run")
    assert res.returncode == 0
    assert "Generated flake.nix" in res.stdout
    assert "rust-overlay" in res.stdout
    assert "cargo-expand" in res.stdout

    # basecamp init snowpack --dry-run
    res = run_basecamp("init", "snowpack", "--dry-run")
    assert res.returncode == 0
    assert "Generated flake.nix" in res.stdout
    assert "typst" in res.stdout

    # basecamp new c --dry-run
    res = run_basecamp("new", "c", "--dry-run")
    assert res.returncode == 0
    assert "Would scaffold" in res.stdout
    assert "main.c" in res.stdout


def test_cli_execution_in_tempdir():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        # Test: basecamp init c --no-direnv --no-git
        res = run_basecamp("init", "c", "--no-direnv", "--no-git", cwd=tmp)
        assert res.returncode == 0
        assert (tmp / "flake.nix").exists()
        assert (tmp / "CMakeLists.txt").exists()
        assert (tmp / "main.c").exists()

        flake_content = (tmp / "flake.nix").read_text()
        assert "gcc" in flake_content
        assert "cmake" in flake_content


def test_cli_project_command():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        # Test: basecamp project c
        res = run_basecamp("project", "c", "--no-git", cwd=tmp)
        assert res.returncode == 0
        assert (tmp / "CMakeLists.txt").exists()
        assert not (tmp / "main.c").exists()


def test_cli_shell_command():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        # Test: basecamp shell rust next --no-git --no-direnv
        res = run_basecamp("shell", "rust", "next", "--no-git", "--no-direnv", cwd=tmp)
        assert res.returncode == 0
        assert (tmp / "flake.nix").exists()
        # Should not scaffold starter files
        assert not (tmp / "Cargo.toml").exists()
        assert not (tmp / "package.json").exists()
        flake_content = (tmp / "flake.nix").read_text()
        assert "rust-overlay" in flake_content
        assert "bun" in flake_content
