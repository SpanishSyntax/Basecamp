import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def run_basecamp(*args: str) -> subprocess.CompletedProcess[str]:
    """Runs Basecamp CLI via subprocess."""
    import os

    env = dict(os.environ)
    existing_pp = os.environ.get("PYTHONPATH", "")
    src_dir = str(REPO_ROOT / "src")
    env["PYTHONPATH"] = f"{src_dir}:{existing_pp}" if existing_pp else src_dir
    cmd = [sys.executable, "-m", "basecamp", *args]
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def test_basecamp_version():
    res = run_basecamp("--version")
    assert res.returncode == 0
    assert "v0.3.0" in res.stdout or "basecamp" in res.stdout


def test_basecamp_help():
    res = run_basecamp("--help")
    assert res.returncode == 0
    assert "Usage:" in res.stdout
    assert "init" in res.stdout
    assert "new" in res.stdout
    assert "shell" in res.stdout
    assert "project" in res.stdout


def test_basecamp_list():
    res = run_basecamp("list")
    assert res.returncode == 0
    assert "Basecamp Roles Registry" in res.stdout
    assert "python" in res.stdout
    assert "rust" in res.stdout
    assert "folio" in res.stdout


def test_basecamp_info_python():
    res = run_basecamp("info", "python")
    assert res.returncode == 0
    assert "Role Information: python" in res.stdout
    assert "python314" in res.stdout


def test_basecamp_info_folio():
    res = run_basecamp("info", "folio")
    assert res.returncode == 0
    assert "Role Information: folio" in res.stdout
    assert "typst" in res.stdout


def test_basecamp_info_invalid():
    res = run_basecamp("info", "nonexistent_role_xyz")
    assert res.returncode != 0
    assert "Unknown role" in res.stderr


def test_basecamp_active_smoke():
    res = run_basecamp("active")
    assert res.returncode == 0
    assert "Active Roles Diagnostic" in res.stdout
