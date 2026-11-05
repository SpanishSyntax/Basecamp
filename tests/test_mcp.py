"""Unit tests for Basecamp MCP server protocol and tool implementations."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from basecamp.mcp import TOOL_DEFINITIONS, StdioMCPServer, execute_tool

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_mcp_initialize() -> None:
    server = StdioMCPServer()
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"},
        },
    }
    resp = server.handle_request(req)
    assert resp is not None
    assert resp["id"] == 1
    assert resp["result"]["serverInfo"]["name"] == "basecamp"
    assert resp["result"]["protocolVersion"] == "2024-11-05"


def test_mcp_ping() -> None:
    server = StdioMCPServer()
    req = {"jsonrpc": "2.0", "id": 42, "method": "ping"}
    resp = server.handle_request(req)
    assert resp == {"jsonrpc": "2.0", "id": 42, "result": {}}


def test_mcp_notifications_initialized() -> None:
    server = StdioMCPServer()
    req = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    resp = server.handle_request(req)
    assert resp is None


def test_mcp_tools_list() -> None:
    server = StdioMCPServer()
    req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    resp = server.handle_request(req)
    assert resp is not None
    tool_names = [t["name"] for t in resp["result"]["tools"]]
    assert "basecamp_list" in tool_names
    assert "basecamp_info" in tool_names
    assert "basecamp_init" in tool_names


def test_mcp_tool_definitions_schema() -> None:
    tools_by_name = {t["name"]: t for t in TOOL_DEFINITIONS}

    # basecamp_list
    assert "basecamp_list" in tools_by_name
    list_props = tools_by_name["basecamp_list"]["inputSchema"]["properties"]
    assert "active_only" in list_props
    assert list_props["active_only"]["type"] == "boolean"

    # basecamp_info
    assert "basecamp_info" in tools_by_name
    info_schema = tools_by_name["basecamp_info"]["inputSchema"]
    assert "role" in info_schema["properties"]
    assert "role" in info_schema["required"]

    # basecamp_init
    assert "basecamp_init" in tools_by_name
    init_schema = tools_by_name["basecamp_init"]["inputSchema"]
    init_props = init_schema["properties"]
    assert "roles" in init_schema["required"]
    assert "mode" in init_props
    assert "engine" in init_props
    assert "title" in init_props
    assert "author" in init_props
    assert "dry_run" in init_props


def test_mcp_execute_unknown() -> None:
    res = execute_tool("nonexistent_tool", {})
    assert res["status"] == "error"
    assert "Unknown tool" in res["error"]


def test_mcp_execute_list() -> None:
    res = execute_tool("basecamp_list", {})
    assert res["status"] == "ok"
    assert "roles" in res
    assert res["count"] > 0

    role_names = [r["role"] for r in res["roles"]]
    assert "python" in role_names
    assert "rust" in role_names
    assert "snowpack" in role_names


def test_mcp_execute_list_active(tmp_path: Path) -> None:
    res = execute_tool(
        "basecamp_list", {"active_only": True, "project_dir": str(tmp_path)}
    )
    assert res["status"] == "ok"
    assert res["active_only"] is True
    assert res["has_flake"] is False


def test_mcp_execute_info_valid() -> None:
    res = execute_tool("basecamp_info", {"role": "python"})
    assert res["status"] == "ok"
    assert res["role"] == "python"
    assert "packages" in res
    assert any("python" in p for p in res["packages"])


def test_mcp_execute_info_snowpack() -> None:
    res = execute_tool("basecamp_info", {"role": "snowpack"})
    assert res["status"] == "ok"
    assert res["role"] == "snowpack"
    assert "typst" in res["packages"]
    assert "tinymist" in res["packages"]


def test_mcp_execute_info_invalid() -> None:
    res = execute_tool("basecamp_info", {"role": "nonexistent_role_xyz"})
    assert res["status"] == "error"
    assert "Unknown role" in res["error"]


def test_mcp_execute_info_missing_arg() -> None:
    res = execute_tool("basecamp_info", {})
    assert res["status"] == "error"
    assert "required" in res["error"]


def test_mcp_execute_init_dry_run() -> None:
    res = execute_tool("basecamp_init", {"roles": "python", "dry_run": True})
    assert res["status"] == "ok"
    assert res["dry_run"] is True
    assert "python" in res["roles"]


def test_mcp_execute_init_scaffold(tmp_path: Path) -> None:
    res = execute_tool(
        "basecamp_init",
        {
            "roles": ["c"],
            "project_dir": str(tmp_path),
        },
    )
    assert res["status"] == "ok"
    assert (tmp_path / "flake.nix").exists()
    assert (tmp_path / "CMakeLists.txt").exists()
    assert (tmp_path / "main.c").exists()

    flake_content = (tmp_path / "flake.nix").read_text()
    assert "gcc" in flake_content

    # Attempting to re-init without force should return an error
    res_conflict = execute_tool(
        "basecamp_init",
        {
            "roles": ["rust"],
            "project_dir": str(tmp_path),
        },
    )
    assert res_conflict["status"] == "error"
    assert "already exists" in res_conflict["error"]

    # Re-init with force should succeed
    res_forced = execute_tool(
        "basecamp_init",
        {
            "roles": ["rust"],
            "project_dir": str(tmp_path),
            "force": True,
        },
    )
    assert res_forced["status"] == "ok"


def test_mcp_execute_init_missing_roles() -> None:
    res = execute_tool("basecamp_init", {})
    assert res["status"] == "error"
    assert "roles" in res["error"]


def test_mcp_tools_call_rpc() -> None:
    server = StdioMCPServer()
    req = {
        "jsonrpc": "2.0",
        "id": 10,
        "method": "tools/call",
        "params": {
            "name": "basecamp_info",
            "arguments": {"role": "rust"},
        },
    }
    resp = server.handle_request(req)
    assert resp is not None
    assert resp["id"] == 10
    result = resp["result"]
    assert result["isError"] is False
    content_text = result["content"][0]["text"]
    data = json.loads(content_text)
    assert data["status"] == "ok"
    assert data["role"] == "rust"


def test_mcp_unknown_method() -> None:
    server = StdioMCPServer()
    req = {"jsonrpc": "2.0", "id": 99, "method": "invalid/method"}
    resp = server.handle_request(req)
    assert resp is not None
    assert "error" in resp
    assert resp["error"]["code"] == -32601


def test_cli_mcp_pipe() -> None:
    import os

    env = dict(os.environ)
    existing_pp = os.environ.get("PYTHONPATH", "")
    src_dir = str(REPO_ROOT / "src")
    env["PYTHONPATH"] = f"{src_dir}:{existing_pp}" if existing_pp else src_dir

    cmd = [sys.executable, "-m", "basecamp", "mcp"]
    p = subprocess.Popen(
        cmd,
        cwd=REPO_ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    input_rpc = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "ping"}) + "\n"
    stdout, stderr = p.communicate(input=input_rpc, timeout=10)
    assert p.returncode == 0
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    assert len(lines) >= 1
    resp = json.loads(lines[0])
    assert resp["id"] == 1
    assert resp["result"] == {}
