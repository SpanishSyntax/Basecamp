import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def run_flaker(*args: str) -> subprocess.CompletedProcess[str]:
    """Runs Flaker CLI via subprocess."""
    cmd = [sys.executable, "-m", "flaker", *args]
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_flaker_version():
    res = run_flaker("--version")
    assert res.returncode == 0
    assert "v0.3.0" in res.stdout or "flaker" in res.stdout


def test_flaker_help():
    res = run_flaker("--help")
    assert res.returncode == 0
    assert "Usage:" in res.stdout
    assert "init" in res.stdout
    assert "new" in res.stdout
    assert "shell" in res.stdout
    assert "project" in res.stdout


def test_flaker_list():
    res = run_flaker("list")
    assert res.returncode == 0
    assert "Flaker Roles Registry" in res.stdout
    assert "python" in res.stdout
    assert "rust" in res.stdout
    assert "folio" in res.stdout


def test_flaker_info_python():
    res = run_flaker("info", "python")
    assert res.returncode == 0
    assert "Role Information: python" in res.stdout
    assert "python314" in res.stdout


def test_flaker_info_folio():
    res = run_flaker("info", "folio")
    assert res.returncode == 0
    assert "Role Information: folio" in res.stdout
    assert "typst" in res.stdout


def test_flaker_info_invalid():
    res = run_flaker("info", "nonexistent_role_xyz")
    assert res.returncode != 0
    assert "Unknown role" in res.stderr
