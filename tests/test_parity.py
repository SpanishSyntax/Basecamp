"""Rigorous parity verification tests comparing against historical specifications."""

import subprocess
import sys
import tempfile
from pathlib import Path

from basecamp.cli.resolver import (
    find_role_for_standalone_target,
    resolve_role_target,
)
from basecamp.core.environment import prepare_flake_env
from basecamp.core.registry import (
    BUILTIN_ALIASES,
    build_builtin_role_registry,
    resolve_nixpkgs_url,
)
from basecamp.scaffold.engine import scaffold_assets
from basecamp.scaffold.manifests import (
    LATEX_PACKAGE_BUNDLES,
    TYPST_PACKAGE_BUNDLES,
    generate_packages_manifest,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = REPO_ROOT / "src" / "basecamp" / "flake.template"
ASSETS_DIR = REPO_ROOT / "src" / "basecamp" / "templates"


def run_basecamp(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
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
        "rust", "c", "cpp", "go", "zig", "java", "dotnet",
        "python", "barograph", "julia", "ts", "svelte", "vue",
        "next", "gleam", "elixir", "haskell", "snowpack", "ops"
    }
    assert expected_roles.issubset(set(roles.keys()))

    # Verify Snowpack targets
    snowpack = roles["snowpack"]
    assert "report" in snowpack.targets
    assert "slides" in snowpack.targets
    assert "paper" in snowpack.targets
    assert "typst-report" in snowpack.targets
    assert "typst-slides" in snowpack.targets
    assert "typst-paper" in snowpack.targets
    assert "latex-report" in snowpack.targets
    assert "latex-slides" in snowpack.targets
    assert "latex-paper" in snowpack.targets


def test_alias_parity():
    # Verify canonical shortcuts
    assert BUILTIN_ALIASES["py"] == "python"
    assert BUILTIN_ALIASES["rs"] == "rust"
    assert BUILTIN_ALIASES["js"] == "ts"
    assert BUILTIN_ALIASES["bg"] == "barograph"
    assert BUILTIN_ALIASES["baro"] == "barograph"
    assert BUILTIN_ALIASES["barograph"] == "barograph"
    assert BUILTIN_ALIASES["snow"] == "snowpack"
    assert BUILTIN_ALIASES["md"] == "snowpack:paper"
    assert BUILTIN_ALIASES["slides"] == "snowpack:slides"
    assert BUILTIN_ALIASES["paper"] == "snowpack:paper"
    assert BUILTIN_ALIASES["report"] == "snowpack:report"
    assert BUILTIN_ALIASES["typ"] == "snowpack:typst-report"
    assert BUILTIN_ALIASES["tex"] == "snowpack:latex-report"
    assert BUILTIN_ALIASES["beamer"] == "snowpack:latex-slides"
    assert BUILTIN_ALIASES["typ:paper"] == "snowpack:typst-paper"
    assert BUILTIN_ALIASES["tex:slides"] == "snowpack:latex-slides"


def test_standalone_target_matching():
    roles = build_builtin_role_registry("test_proj")
    assert find_role_for_standalone_target("slides", roles) == ("snowpack", "slides")
    assert find_role_for_standalone_target("paper", roles) == ("snowpack", "paper")
    assert find_role_for_standalone_target("report", roles) == ("snowpack", "report")
    assert find_role_for_standalone_target("typst-paper", roles) == ("snowpack", "typst-paper")
    assert find_role_for_standalone_target("latex-slides", roles) == ("snowpack", "latex-slides")


def test_cli_dry_run_parity():
    # basecamp init rust --dry-run
    res = run_basecamp("init", "rust", "--dry-run")
    assert res.returncode == 0
    assert "Generated flake.nix" in res.stdout
    assert "rust-overlay" in res.stdout
    assert "cargo-expand" in res.stdout

    # basecamp init snowpack slides --dry-run
    res = run_basecamp("init", "snowpack", "slides", "--dry-run")
    assert res.returncode == 0
    assert "Generated flake.nix" in res.stdout
    assert "typst" in res.stdout

    # basecamp new slides --dry-run
    res = run_basecamp("new", "slides", "--dry-run")
    assert res.returncode == 0
    assert "Would scaffold" in res.stdout
    assert "slides.md" in res.stdout

    # basecamp new typ:paper --dry-run
    res = run_basecamp("new", "typ:paper", "--dry-run")
    assert res.returncode == 0
    assert "Would scaffold" in res.stdout
    assert "paper.typ" in res.stdout

    # basecamp new tex:slides --dry-run
    res = run_basecamp("new", "tex:slides", "--dry-run")
    assert res.returncode == 0
    assert "Would scaffold" in res.stdout
    assert "slides.tex" in res.stdout


def test_cli_execution_in_tempdir():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        # Test: basecamp init py --no-direnv --no-git
        res = run_basecamp("init", "py", "--no-direnv", "--no-git", cwd=tmp)
        assert res.returncode == 0
        assert (tmp / "flake.nix").exists()
        assert (tmp / "pyproject.toml").exists()
        assert (tmp / "main.py").exists()

        flake_content = (tmp / "flake.nix").read_text()
        assert "python3" in flake_content
        assert "uv" in flake_content

        pyproject_content = (tmp / "pyproject.toml").read_text()
        assert 'name = "' in pyproject_content


def test_cli_project_command():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        # Test: basecamp project snowpack
        res = run_basecamp("project", "snowpack", "--no-git", cwd=tmp)
        assert res.returncode == 0
        # Project assets for snowpack include packages.typ, report.typ, library.bib
        assert (tmp / "packages.typ").exists()
        assert (tmp / "library.bib").exists()
        assert not (tmp / "main.py").exists()


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
