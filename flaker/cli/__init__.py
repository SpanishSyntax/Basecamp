"""Flaker CLI interface and public symbol exports."""

from flaker.cli.resolver import (
    find_role_for_standalone_target,
    resolve_role_target,
)
from flaker.cli.router import main
from flaker.core.environment import prepare_flake_env
from flaker.core.models import Role
from flaker.core.registry import (
    BUILTIN_ALIASES,
    build_builtin_role_registry,
    resolve_nixpkgs_url,
)
from flaker.scaffold.engine import scaffold_assets
from flaker.scaffold.git import update_gitignore
from flaker.scaffold.manifests import generate_packages_manifest

__all__ = [
    "main",
    "Role",
    "build_builtin_role_registry",
    "BUILTIN_ALIASES",
    "resolve_role_target",
    "find_role_for_standalone_target",
    "resolve_nixpkgs_url",
    "generate_packages_manifest",
    "prepare_flake_env",
    "scaffold_assets",
    "update_gitignore",
]
