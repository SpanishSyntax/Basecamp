import tempfile
from pathlib import Path

from basecamp.cli import (
    build_builtin_role_registry,
    prepare_flake_env,
    scaffold_assets,
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
        assert "python3" in content
        assert "github:NixOS/nixpkgs/nixos-26.05" in content

        gitignore_content = gitignore_file.read_text()
        assert ".direnv/" in gitignore_content
        assert "target/" in gitignore_content
        assert ".venv/" in gitignore_content


def test_scaffold_c_assets():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        roles = build_builtin_role_registry("test_c")
        scaffold_assets(
            target_dir=tmp_path,
            project_name="test_c",
            resolved_roles=["c"],
            assets_dirs=[ASSETS_DIR],
            scope="all",
            force=True,
            dry_run=False,
            auto_git=False,
            project_root=tmp_path,
            roles_db=roles,
        )
        assert (tmp_path / "CMakeLists.txt").exists()
        assert (tmp_path / "main.c").exists()
        cmake_content = (tmp_path / "CMakeLists.txt").read_text()
        assert "test_c" in cmake_content


def test_scaffold_cpp_assets():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        roles = build_builtin_role_registry("test_cpp")
        scaffold_assets(
            target_dir=tmp_path,
            project_name="test_cpp",
            resolved_roles=["cpp"],
            assets_dirs=[ASSETS_DIR],
            scope="all",
            force=True,
            dry_run=False,
            auto_git=False,
            project_root=tmp_path,
            roles_db=roles,
        )
        assert (tmp_path / "CMakeLists.txt").exists()
        assert (tmp_path / "main.cpp").exists()
        cmake_content = (tmp_path / "CMakeLists.txt").read_text()
        assert "test_cpp" in cmake_content


def test_scaffold_ops_assets():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        roles = build_builtin_role_registry("test_ops")
        scaffold_assets(
            target_dir=tmp_path,
            project_name="test_ops",
            resolved_roles=["ops"],
            assets_dirs=[ASSETS_DIR],
            scope="project",
            force=True,
            dry_run=False,
            auto_git=False,
            project_root=tmp_path,
            roles_db=roles,
        )
        assert (tmp_path / "compose.yaml").exists()
