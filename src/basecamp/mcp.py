"""Model Context Protocol (MCP) server for Basecamp."""

from __future__ import annotations

import contextlib
import io
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from basecamp import __version__
from basecamp.cli.commands.active import diagnose_flake
from basecamp.cli.resolver import resolve_role_target
from basecamp.core.config import load_user_config
from basecamp.core.environment import (
    find_project_root,
    get_project_name,
    prepare_flake_env,
)
from basecamp.core.registry import (
    BUILTIN_ALIASES,
    build_builtin_role_registry,
    resolve_nixpkgs_url,
)
from basecamp.scaffold.engine import resolve_metadata, scaffold_assets

BASECAMP_DIR = Path(__file__).resolve().parent
FALLBACK_TEMPLATE = BASECAMP_DIR / "flake.template"
FALLBACK_ASSETS = BASECAMP_DIR / "templates"
DEFAULT_RUNTIME_LIBS = "stdenv.cc.cc.lib,zlib,glib,libxml2,openssl,libffi"

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "basecamp_list",
        "description": "Lists all available development shell roles and categories, or inspects active roles in the current flake workspace.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "active_only": {
                    "type": "boolean",
                    "description": "If true, only returns active roles detected in the current workspace flake.nix (default: false).",
                    "default": False,
                },
                "project_dir": {
                    "type": "string",
                    "description": "Optional project root directory path (default: current directory).",
                },
            },
        },
    },
    {
        "name": "basecamp_info",
        "description": "Queries detailed package lists, shell hooks, document targets, and starter templates for a Basecamp role.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "role": {
                    "type": "string",
                    "description": "Role name or alias to query (e.g. 'python', 'rust', 'typst', 'snowpack', 'ops').",
                },
            },
            "required": ["role"],
        },
    },
    {
        "name": "basecamp_init",
        "description": "Scaffolds a polyglot Nix DevShell (flake.nix), .envrc, and starter files via Basecamp.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "roles": {
                    "description": "Role name(s) to bootstrap (e.g. 'python', ['rust', 'snowpack'], 'snowpack:slides').",
                    "oneOf": [
                        {"type": "string"},
                        {"type": "array", "items": {"type": "string"}},
                    ],
                },
                "mode": {
                    "type": "string",
                    "description": "Document operating mode / target (e.g. 'report', 'slides', 'paper'). Default is 'report'.",
                    "default": "report",
                },
                "engine": {
                    "type": "string",
                    "description": "Compilation engine for Markdown documents ('typst' or 'latex'). Default is 'typst'.",
                    "default": "typst",
                },
                "title": {
                    "type": "string",
                    "description": "Document title for Snowpack documents.",
                    "default": "",
                },
                "author": {
                    "type": "string",
                    "description": "Document author for Snowpack documents.",
                    "default": "",
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "Preview generated files without writing them to disk (default: false).",
                    "default": False,
                },
                "project_dir": {
                    "type": "string",
                    "description": "Target project directory to bootstrap (default: current directory).",
                },
                "force": {
                    "type": "boolean",
                    "description": "Overwrite existing files without confirmation prompts (default: false).",
                    "default": False,
                },
                "no_direnv": {
                    "type": "boolean",
                    "description": "Skip generating .envrc and direnv hooks (default: false).",
                    "default": False,
                },
                "channel": {
                    "type": "string",
                    "description": "Nixpkgs channel (default: nixos-26.05).",
                },
            },
            "required": ["roles"],
        },
    },
]


def _normalize_roles(roles: Any) -> list[str]:
    """Flattens and normalizes role inputs provided as string or list."""
    if isinstance(roles, str):
        return [r.strip() for r in re.split(r"[,\s]+", roles) if r.strip()]
    elif isinstance(roles, (list, tuple)):
        result: list[str] = []
        for item in roles:
            if isinstance(item, str):
                for part in re.split(r"[,\s]+", item):
                    if part.strip():
                        result.append(part.strip())
        return result
    return []


def _handle_list(active_only: bool = False, project_dir: str = ".") -> dict[str, Any]:
    target_path = Path(project_dir).expanduser().resolve()
    project_root = find_project_root(target_path)
    project_name = get_project_name(project_root)

    user_roles, user_aliases, _ = load_user_config()
    roles_db = build_builtin_role_registry(project_name)
    roles_db.update(user_roles)

    aliases = dict(BUILTIN_ALIASES)
    aliases.update(user_aliases)

    if active_only:
        diag = diagnose_flake(project_root, roles_db, aliases)
        has_flake = diag.flake_path.exists()
        return {
            "status": "ok",
            "active_only": True,
            "project_root": str(diag.project_root),
            "flake_path": str(diag.flake_path) if has_flake else None,
            "has_flake": has_flake,
            "channel": diag.channel,
            "active_roles": [
                {
                    "role": r.role_key,
                    "category": r.role.category,
                    "description": r.role.description,
                    "detection_method": r.detection_method,
                    "packages": r.role.pkgs,
                }
                for r in diag.active_roles
            ],
            "extra_packages": diag.extra_packages,
            "discovered_artifacts": diag.discovered_artifacts,
        }

    roles_data = [
        {
            "role": r_key,
            "category": role.category,
            "description": role.description,
            "aliases": sorted([a for a, target in aliases.items() if target == r_key]),
            "packages": role.pkgs,
            "targets": list(role.targets.keys()) if role.targets else [],
        }
        for r_key, role in sorted(roles_db.items())
    ]
    return {
        "status": "ok",
        "count": len(roles_data),
        "roles": roles_data,
    }


def _handle_info(role: str) -> dict[str, Any]:
    if not role or not role.strip():
        return {
            "status": "error",
            "error": "'role' argument is required and cannot be empty.",
        }

    current_dir = Path.cwd()
    project_root = find_project_root(current_dir)
    project_name = get_project_name(project_root)

    user_roles, user_aliases, custom_asset_dirs = load_user_config()
    assets_dir_env = os.environ.get("BASECAMP_ASSETS")
    primary_assets_dir = Path(assets_dir_env) if assets_dir_env else FALLBACK_ASSETS
    all_asset_dirs = custom_asset_dirs + [primary_assets_dir]

    roles_db = build_builtin_role_registry(project_name)
    roles_db.update(user_roles)

    aliases = dict(BUILTIN_ALIASES)
    aliases.update(user_aliases)

    clean_input = role.strip().lower()
    aliased_target = aliases.get(clean_input, clean_input)
    resolved_name = aliased_target.split(":", 1)[0]

    if resolved_name not in roles_db:
        return {
            "status": "error",
            "error": f"Unknown role '{role}'. Available roles: {', '.join(sorted(roles_db.keys()))}",
        }

    role_def = roles_db[resolved_name]
    rev_aliases = [a for a, t in aliases.items() if t == resolved_name]

    project_files: list[str] = []
    starter_files: list[str] = []
    for adir in all_asset_dirs:
        rdir = adir / resolved_name
        if rdir.exists():
            pdir = rdir / "project"
            sdir = rdir / "starter"
            if pdir.exists() or sdir.exists():
                if pdir.exists():
                    for f in pdir.glob("**/*"):
                        if (
                            f.is_file()
                            and "__pycache__" not in f.parts
                            and f.suffix not in (".pyc", ".pyo")
                        ):
                            project_files.append(str(f.relative_to(pdir)))
                if sdir.exists():
                    for f in sdir.glob("**/*"):
                        if (
                            f.is_file()
                            and "__pycache__" not in f.parts
                            and f.suffix not in (".pyc", ".pyo")
                        ):
                            starter_files.append(str(f.relative_to(sdir)))
            else:
                for f in rdir.glob("**/*"):
                    if (
                        f.is_file()
                        and "__pycache__" not in f.parts
                        and f.suffix not in (".pyc", ".pyo")
                    ):
                        starter_files.append(str(f.relative_to(rdir)))
            break

    return {
        "status": "ok",
        "role": resolved_name,
        "category": role_def.category,
        "description": role_def.description,
        "aliases": sorted(rev_aliases),
        "packages": role_def.pkgs,
        "hooks": role_def.hooks,
        "targets": role_def.targets,
        "ignores": role_def.ignores,
        "project_files": sorted(project_files),
        "starter_files": sorted(starter_files),
    }


def _handle_init(
    roles: Any,
    mode: str = "report",
    engine: str = "typst",
    title: str = "",
    author: str = "",
    dry_run: bool = False,
    project_dir: str = ".",
    force: bool = False,
    no_direnv: bool = False,
    channel: str | None = None,
) -> dict[str, Any]:
    raw_roles = _normalize_roles(roles)
    if not raw_roles:
        return {
            "status": "error",
            "error": "'roles' argument is required and cannot be empty.",
        }

    target_dir = Path(project_dir).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    project_name = get_project_name(target_dir)

    user_roles, user_aliases, custom_asset_dirs = load_user_config()
    assets_dir_env = os.environ.get("BASECAMP_ASSETS")
    primary_assets_dir = Path(assets_dir_env) if assets_dir_env else FALLBACK_ASSETS
    all_asset_dirs = custom_asset_dirs + [primary_assets_dir]

    template_path_env = os.environ.get("FLAKE_TEMPLATE")
    template_path = Path(template_path_env) if template_path_env else FALLBACK_TEMPLATE
    if not template_path.exists():
        return {
            "status": "error",
            "error": f"Flake template file not found: {template_path}",
        }

    roles_db = build_builtin_role_registry(project_name)
    roles_db.update(user_roles)

    aliases = dict(BUILTIN_ALIASES)
    aliases.update(user_aliases)

    resolved_roles: list[str] = []
    role_targets: dict[str, str] = {}

    for item in raw_roles:
        raw_lower = item.lower()

        # Direct alias with colon target (e.g. md:report -> snowpack:report)
        if raw_lower in aliases and ":" in aliases[raw_lower]:
            r_part, _, t_part = aliases[raw_lower].partition(":")
            canonical_role = aliases.get(r_part.lower(), r_part.lower()).split(":", 1)[
                0
            ]
            resolved_t = resolve_role_target(canonical_role, t_part, roles_db) or t_part
            if canonical_role in roles_db:
                role_targets[canonical_role] = resolved_t
                if canonical_role not in resolved_roles:
                    resolved_roles.append(canonical_role)
                continue

        # Item with explicit colon (e.g. snowpack:slides)
        if ":" in item:
            r_part, _, t_part = item.partition(":")
            canonical_role = aliases.get(r_part.lower(), r_part.lower()).split(":", 1)[
                0
            ]
            if canonical_role in roles_db and roles_db[canonical_role].targets:
                composite = f"{r_part.lower()}-{t_part.lower()}"
                resolved_t = resolve_role_target(
                    canonical_role, composite, roles_db
                ) or resolve_role_target(canonical_role, t_part, roles_db)
                role_targets[canonical_role] = resolved_t or t_part
            if canonical_role not in resolved_roles:
                resolved_roles.append(canonical_role)
            continue

        # Normal role name or alias
        aliased_val = aliases.get(raw_lower, raw_lower)
        canonical_role = aliased_val.split(":", 1)[0]
        if ":" in aliased_val:
            target_part = aliased_val.split(":", 1)[1]
            resolved_t = (
                resolve_role_target(canonical_role, target_part, roles_db)
                or target_part
            )
            role_targets[canonical_role] = resolved_t
        if canonical_role not in resolved_roles:
            resolved_roles.append(canonical_role)

    # Apply default or user-specified mode to roles that support targets
    for r in resolved_roles:
        if r in roles_db and roles_db[r].targets and r not in role_targets:
            resolved_t = resolve_role_target(r, mode, roles_db) or mode
            role_targets[r] = resolved_t

    flake_out = target_dir / "flake.nix"
    if flake_out.exists() and not force and not dry_run:
        return {
            "status": "error",
            "error": f"flake.nix already exists at {target_dir}. Pass force=true to overwrite.",
        }

    nixpkgs_url = resolve_nixpkgs_url(channel)
    libs_list = os.environ.get("LIBS_LIST", DEFAULT_RUNTIME_LIBS).replace(",", " ")

    doc_metadata = resolve_metadata(
        project_name=project_name,
        author_flag=author or None,
    )

    stdout_capture = io.StringIO()
    with contextlib.redirect_stdout(stdout_capture):
        # 1. DevShell generation
        prepare_flake_env(
            project_root=target_dir,
            resolved_roles=resolved_roles,
            roles_db=roles_db,
            template_path=template_path,
            libs_list=libs_list,
            nixpkgs_url=nixpkgs_url,
            force=force,
            dry_run=dry_run,
            auto_git=True,
            no_direnv=no_direnv,
        )

        # 2. Project foundation scaffolding
        scaffold_assets(
            target_dir=target_dir,
            project_name=project_name,
            resolved_roles=resolved_roles,
            assets_dirs=all_asset_dirs,
            scope="project",
            force=force,
            dry_run=dry_run,
            auto_git=True,
            project_root=target_dir,
            role_targets=role_targets,
            roles_db=roles_db,
            metadata=doc_metadata,
        )

        # 3. Starter files scaffolding
        scaffold_assets(
            target_dir=target_dir,
            project_name=project_name,
            resolved_roles=resolved_roles,
            assets_dirs=all_asset_dirs,
            scope="starter",
            force=force,
            dry_run=dry_run,
            auto_git=True,
            project_root=target_dir,
            role_targets=role_targets,
            roles_db=roles_db,
            metadata=doc_metadata,
        )

    files_created: list[str] = []
    if not dry_run:
        for p in [
            target_dir / "flake.nix",
            target_dir / ".envrc",
            target_dir / ".gitignore",
        ]:
            if p.exists():
                files_created.append(str(p.relative_to(target_dir)))
        for item in target_dir.rglob("*"):
            if item.is_file():
                rel = str(item.relative_to(target_dir))
                if rel not in files_created and not any(
                    part.startswith(".") for part in item.relative_to(target_dir).parts
                ):
                    files_created.append(rel)

    return {
        "status": "ok",
        "project_dir": str(target_dir),
        "roles": resolved_roles,
        "targets": role_targets,
        "mode": mode,
        "engine": engine,
        "dry_run": dry_run,
        "files_created": sorted(files_created) if not dry_run else [],
        "output": stdout_capture.getvalue().strip(),
    }


def execute_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute a Basecamp MCP tool call and return JSON-serializable results."""
    try:
        if name == "basecamp_list":
            active_only = arguments.get("active_only", False)
            project_dir = arguments.get("project_dir", ".")
            return _handle_list(active_only=active_only, project_dir=project_dir)

        elif name == "basecamp_info":
            role = arguments.get("role", "")
            return _handle_info(role=role)

        elif name == "basecamp_init":
            roles = arguments.get("roles")
            mode = arguments.get("mode", "report")
            engine = arguments.get("engine", "typst")
            title = arguments.get("title", "")
            author = arguments.get("author", "")
            dry_run = arguments.get("dry_run", False)
            project_dir = arguments.get("project_dir", ".")
            force = arguments.get("force", False)
            no_direnv = arguments.get("no_direnv", False)
            channel = arguments.get("channel")
            return _handle_init(
                roles=roles,
                mode=mode,
                engine=engine,
                title=title,
                author=author,
                dry_run=dry_run,
                project_dir=project_dir,
                force=force,
                no_direnv=no_direnv,
                channel=channel,
            )

        else:
            return {"status": "error", "error": f"Unknown tool: {name}"}

    except Exception as e:
        return {"status": "error", "error": str(e)}


class StdioMCPServer:
    """JSON-RPC 2.0 stdio server implementing the Model Context Protocol."""

    def __init__(self) -> None:
        self.server_info = {"name": "basecamp", "version": __version__}

    def handle_request(self, req: dict[str, Any]) -> dict[str, Any] | None:
        method = req.get("method")
        msg_id = req.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": self.server_info,
                    "capabilities": {"tools": {}},
                },
            }

        elif method == "notifications/initialized":
            return None

        elif method == "ping":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": TOOL_DEFINITIONS},
            }

        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name", "")
            args = params.get("arguments", {})
            res = execute_tool(name, args)
            is_error = res.get("status") == "error"

            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(res, indent=2)}],
                    "isError": is_error,
                },
            }

        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }

    def run(self) -> int:
        """Run JSON-RPC event loop reading lines from sys.stdin."""
        for line in sys.stdin:
            line_str = line.strip()
            if not line_str:
                continue
            try:
                req = json.loads(line_str)
                resp = self.handle_request(req)
                if resp is not None:
                    sys.stdout.write(json.dumps(resp) + "\n")
                    sys.stdout.flush()
            except Exception as e:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {e}"},
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()
        return 0


def main() -> int:
    """Entry point for basecamp mcp."""
    return StdioMCPServer().run()


if __name__ == "__main__":
    sys.exit(main())
