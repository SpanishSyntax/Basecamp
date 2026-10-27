from pathlib import Path
import tempfile
from basecamp.cli import (
    build_builtin_role_registry,
    prepare_flake_env,
    scaffold_assets,
    update_gitignore,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = REPO_ROOT / "src" / "basecamp" / "flake.template"
ASSETS_DIR = REPO_ROOT / "src" / "basecamp" / "templates"


def test_prepare_flake_env():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        roles = build_builtin_role_registry("test_proj")
        success = prepare_flake_env(
            project_root=tmp_path,
            resolved_roles=["rust", "python"],
            roles_db=roles,
            template_path=TEMPLATE_PATH,
            libs_list="stdenv.cc.cc.lib zlib",
            nixpkgs_url="github:NixOS/nixpkgs/nixos-26.05",
            force=True,
            dry_run=False,
            auto_git=False,
            no_direnv=False,
        )
        assert success is True
        flake_file = tmp_path / "flake.nix"
        envrc_file = tmp_path / ".envrc"
        gitignore_file = tmp_path / ".gitignore"

        assert flake_file.exists()
        assert envrc_file.exists()
        assert gitignore_file.exists()

        content = flake_file.read_text()
        assert "rust-overlay" in content
        assert "python314" in content
        assert "github:NixOS/nixpkgs/nixos-26.05" in content

        gitignore_content = gitignore_file.read_text()
        assert ".direnv/" in gitignore_content
        assert "target/" in gitignore_content
        assert ".venv/" in gitignore_content


def test_scaffold_python_assets():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        roles = build_builtin_role_registry("test_proj")
        # Project assets (pyproject.toml)
        scaffold_assets(
            target_dir=tmp_path,
            project_name="test_proj",
            resolved_roles=["python"],
            assets_dirs=[ASSETS_DIR],
            scope="project",
            force=True,
            dry_run=False,
            auto_git=False,
            project_root=tmp_path,
            roles_db=roles,
        )
        assert (tmp_path / "pyproject.toml").exists()
        content = (tmp_path / "pyproject.toml").read_text()
        assert 'name = "test_proj"' in content

        # Starter assets (main.py)
        scaffold_assets(
            target_dir=tmp_path,
            project_name="test_proj",
            resolved_roles=["python"],
            assets_dirs=[ASSETS_DIR],
            scope="starter",
            force=True,
            dry_run=False,
            auto_git=False,
            project_root=tmp_path,
            roles_db=roles,
        )
        assert (tmp_path / "main.py").exists()


def test_scaffold_folio_slides():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        roles = build_builtin_role_registry("test_slides")
        role_targets = {"folio": "slides"}
        metadata = {
            "title": "Quantum Control",
            "author": "Dr. Marie",
            "theme": "dark",
            "engine": "typst",
        }
        # Starter assets (slides.md)
        scaffold_assets(
            target_dir=tmp_path,
            project_name="test_slides",
            resolved_roles=["folio"],
            assets_dirs=[ASSETS_DIR],
            scope="starter",
            force=True,
            dry_run=False,
            auto_git=False,
            project_root=tmp_path,
            role_targets=role_targets,
            roles_db=roles,
            metadata=metadata,
        )
        slides_file = tmp_path / "slides.md"
        assert slides_file.exists()
        content = slides_file.read_text()
        assert "Quantum Control" in content
        assert "Dr. Marie" in content


def test_scaffold_barograph_assets():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        roles = build_builtin_role_registry("test_bg")
        scaffold_assets(
            target_dir=tmp_path,
            project_name="test_bg",
            resolved_roles=["barograph"],
            assets_dirs=[ASSETS_DIR],
            scope="all",
            force=True,
            dry_run=False,
            auto_git=False,
            project_root=tmp_path,
            roles_db=roles,
        )
        assert (tmp_path / "pyproject.toml").exists()
        assert (tmp_path / "plot.py").exists()
        assert (tmp_path / "dashboard.py").exists()
        dash_content = (tmp_path / "dashboard.py").read_text()
        assert "Barograph" in dash_content
        assert "test_bg" in dash_content

