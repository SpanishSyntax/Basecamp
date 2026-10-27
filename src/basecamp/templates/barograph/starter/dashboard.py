"""📈 Barograph Interactive Simulation Hub & Landing Page Dashboard.

This script scans the workspace for standalone plotting scripts (`plot*.py`),
extracts metadata, and compiles an interactive multi-view landing page dashboard.
Each plot runs in its own isolated `plot_*.py` file, while `dashboard.py`
aggregates and presents them with live-reloading, grid overview, and hero stage view.

Run with Barograph:
    barograph serve dashboard.py
    # or simply:
    barograph serve
"""

from __future__ import annotations

import ast
import html
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_NAME = "__PROJECT_NAME__"
PROJECT_DIR = Path(__file__).resolve().parent


class PlotScriptMeta:
    """Metadata extracted from a standalone plotting script."""

    def __init__(self, path: Path, base_dir: Path):
        self.path = path
        self.rel_path = path.relative_to(base_dir).as_posix()
        self.name = path.name
        self.size_kb = path.stat().st_size / 1024.0
        self.mtime = path.stat().st_mtime
        self.title, self.description = self._extract_docstring_and_title()

    def _extract_docstring_and_title(self) -> tuple[str, str]:
        title = self.name.replace(".py", "").replace("plot_", "").replace("plot", "Main Plot").replace("_", " ").title()
        description = ""
        try:
            content = self.path.read_text(encoding="utf-8")
            tree = ast.parse(content)
            doc = ast.get_docstring(tree)
            if doc:
                lines = [ln.strip() for ln in doc.splitlines() if ln.strip()]
                if lines:
                    title = lines[0]
                    if len(lines) > 1:
                        description = " ".join(lines[1:])
            else:
                for line in content.splitlines()[:15]:
                    line = line.strip()
                    if line.startswith("#") and not line.startswith("#!"):
                        candidate = line.lstrip("#").strip()
                        if candidate and not candidate.startswith("---") and not candidate.startswith("Build"):
                            title = candidate
                            break
        except Exception:
            pass
        return title, description

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "rel_path": self.rel_path,
            "title": self.title,
            "description": self.description,
            "size_kb": f"{self.size_kb:.1f}",
            "mtime": self.mtime,
        }


def discover_plot_scripts(base_dir: Path) -> list[PlotScriptMeta]:
    """Discover all plotting scripts in workspace except dashboard.py."""
    candidates: list[Path] = []
    # 1. Check for standard plot.py first
    std_plot = base_dir / "plot.py"
    if std_plot.is_file():
        candidates.append(std_plot)

    # 2. Check for other plot*.py scripts
    for item in sorted(base_dir.glob("plot*.py")):
        if item.is_file() and item.name != "dashboard.py" and item not in candidates:
            candidates.append(item)

    # 3. Check for plots/*.py subfolder
    plots_dir = base_dir / "plots"
    if plots_dir.is_dir():
        for item in sorted(plots_dir.glob("*.py")):
            if item.is_file() and not item.name.startswith(".") and item not in candidates:
                candidates.append(item)

    return [PlotScriptMeta(p, base_dir) for p in candidates]


def generate_dashboard_html(project_name: str, scripts: list[PlotScriptMeta]) -> str:
    """Generate the Frost-themed landing page dashboard HTML."""
    scripts_json = json.dumps([s.to_dict() for s in scripts])
    default_active = scripts[0].rel_path if scripts else ""

    cards_html = ""
    for s in scripts:
        escaped_title = html.escape(s.title)
        escaped_name = html.escape(s.name)
        escaped_rel = html.escape(s.rel_path)
        cards_html += f"""
        <div class="plot-card" data-script="{escaped_rel}">
          <div class="plot-card-header">
            <div class="plot-card-info">
              <span class="plot-card-badge">LIVE SCRIPT</span>
              <h3 class="plot-card-title">{escaped_title}</h3>
              <span class="plot-card-filename">{escaped_name}</span>
            </div>
            <div class="plot-card-actions">
              <button class="btn-icon" title="Focus View" onclick="selectScript('{escaped_rel}', true)">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>
              </button>
              <a class="btn-icon" title="Open Raw Standalone" href="/{escaped_rel}" target="_blank">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/></svg>
              </a>
            </div>
          </div>
          <div class="plot-card-viewport">
            <iframe class="plot-card-frame" src="/{escaped_rel}" loading="lazy" title="{escaped_title}"></iframe>
          </div>
          <div class="plot-card-footer">
            <span class="footer-meta">📁 {escaped_rel}</span>
            <span class="footer-meta">⚡ {s.size_kb:.1f} KB</span>
          </div>
        </div>
        """

    sidebar_items_html = ""
    for idx, s in enumerate(scripts):
        escaped_title = html.escape(s.title)
        escaped_name = html.escape(s.name)
        escaped_rel = html.escape(s.rel_path)
        active_class = "active" if idx == 0 else ""
        sidebar_items_html += f"""
        <button class="script-item {active_class}" data-script="{escaped_rel}" onclick="selectScript('{escaped_rel}', true)">
          <div class="script-item-dot"></div>
          <div class="script-item-text">
            <div class="script-item-title">{escaped_title}</div>
            <div class="script-item-sub">{escaped_name} ({s.size_kb:.1f} KB)</div>
          </div>
        </button>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(project_name)} — Barograph Hub</title>
  <style>
    :root {{
      --bg: #090d14;
      --surface: #101622;
      --surface-elevated: #161f30;
      --border: #212c42;
      --border-accent: #00d2ff33;
      --text: #f0f4f8;
      --text-muted: #8b9bb4;
      --accent: #00d2ff;
      --accent-glow: rgba(0, 210, 255, 0.2);
      --success: #10b981;
      --purple: #a855f7;
      --sidebar-width: 320px;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }}
    /* Header */
    header {{
      height: 60px;
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 1.5rem;
      z-index: 20;
    }}
    .logo-group {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}
    .brand-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      background: linear-gradient(135deg, rgba(0,210,255,0.15), rgba(168,85,247,0.15));
      border: 1px solid var(--border-accent);
      padding: 0.3rem 0.65rem;
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--accent);
      letter-spacing: 0.05em;
    }}
    .project-title {{
      font-size: 1.05rem;
      font-weight: 600;
      color: #fff;
    }}
    .header-actions {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}
    .status-pill {{
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.25);
      color: var(--success);
      font-size: 0.75rem;
      font-weight: 600;
      padding: 0.25rem 0.65rem;
      border-radius: 999px;
    }}
    .pulse-dot {{
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--success);
      box-shadow: 0 0 8px var(--success);
      animation: pulse 2s infinite ease-in-out;
    }}
    @keyframes pulse {{
      0%, 100% {{ opacity: 1; transform: scale(1); }}
      50% {{ opacity: 0.4; transform: scale(0.85); }}
    }}
    .view-toggle {{
      display: flex;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 3px;
    }}
    .view-toggle button {{
      background: none;
      border: none;
      color: var(--text-muted);
      padding: 0.35rem 0.75rem;
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}
    .view-toggle button.active {{
      background: var(--surface-elevated);
      color: var(--accent);
      box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }}
    /* Main Layout */
    .layout {{
      display: flex;
      flex: 1;
      height: calc(100vh - 60px);
      overflow: hidden;
    }}
    /* Sidebar */
    aside {{
      width: var(--sidebar-width);
      background: var(--surface);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      z-index: 10;
    }}
    .sidebar-search {{
      padding: 1rem;
      border-bottom: 1px solid var(--border);
    }}
    .search-input {{
      width: 100%;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 6px;
      color: var(--text);
      padding: 0.5rem 0.75rem;
      font-size: 0.82rem;
      outline: none;
      transition: border-color 0.2s;
    }}
    .search-input:focus {{
      border-color: var(--accent);
    }}
    .sidebar-list {{
      flex: 1;
      overflow-y: auto;
      padding: 0.5rem;
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
    }}
    .script-item {{
      background: transparent;
      border: 1px solid transparent;
      border-radius: 8px;
      padding: 0.65rem 0.75rem;
      text-align: left;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.65rem;
      transition: all 0.15s ease;
      width: 100%;
    }}
    .script-item:hover {{
      background: var(--surface-elevated);
      border-color: var(--border);
    }}
    .script-item.active {{
      background: linear-gradient(90deg, rgba(0,210,255,0.08), rgba(0,210,255,0.02));
      border-color: var(--border-accent);
    }}
    .script-item-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--border);
      flex-shrink: 0;
      transition: all 0.2s;
    }}
    .script-item.active .script-item-dot {{
      background: var(--accent);
      box-shadow: 0 0 8px var(--accent);
    }}
    .script-item-text {{
      flex: 1;
      min-width: 0;
    }}
    .script-item-title {{
      font-size: 0.85rem;
      font-weight: 600;
      color: #fff;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .script-item-sub {{
      font-size: 0.72rem;
      color: var(--text-muted);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      margin-top: 2px;
    }}
    .sidebar-footer {{
      padding: 0.85rem 1rem;
      border-top: 1px solid var(--border);
      background: var(--bg);
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.75rem;
      color: var(--text-muted);
    }}
    /* Main View Area */
    main {{
      flex: 1;
      height: 100%;
      overflow-y: auto;
      background: var(--bg);
      position: relative;
    }}
    /* Focus Stage Mode */
    #stage-view {{
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
    }}
    .stage-toolbar {{
      height: 48px;
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 1.25rem;
    }}
    .stage-title {{
      display: flex;
      align-items: center;
      gap: 0.6rem;
      font-size: 0.88rem;
      font-weight: 600;
      color: #fff;
    }}
    .stage-actions {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}
    .stage-frame-container {{
      flex: 1;
      width: 100%;
      height: calc(100% - 48px);
      position: relative;
    }}
    .stage-frame {{
      width: 100%;
      height: 100%;
      border: none;
      display: block;
      background: #000;
    }}
    /* Grid Overview Mode */
    #grid-view {{
      padding: 1.5rem;
      display: none;
      grid-template-columns: repeat(auto-fill, minmax(520px, 1fr));
      gap: 1.5rem;
    }}
    .plot-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
      transition: transform 0.2s, border-color 0.2s;
    }}
    .plot-card:hover {{
      border-color: var(--border-accent);
      transform: translateY(-2px);
    }}
    .plot-card-header {{
      padding: 0.85rem 1rem;
      background: var(--surface-elevated);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .plot-card-info {{
      min-width: 0;
      flex: 1;
    }}
    .plot-card-badge {{
      display: inline-block;
      font-size: 0.65rem;
      font-weight: 700;
      color: var(--accent);
      letter-spacing: 0.05em;
      margin-bottom: 2px;
    }}
    .plot-card-title {{
      font-size: 0.92rem;
      font-weight: 600;
      color: #fff;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .plot-card-filename {{
      font-size: 0.72rem;
      color: var(--text-muted);
      font-family: monospace;
    }}
    .plot-card-actions {{
      display: flex;
      gap: 0.35rem;
    }}
    .btn-icon {{
      background: var(--bg);
      border: 1px solid var(--border);
      color: var(--text-muted);
      width: 32px;
      height: 32px;
      border-radius: 6px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      text-decoration: none;
      transition: all 0.15s;
    }}
    .btn-icon:hover {{
      color: #fff;
      border-color: var(--accent);
      background: var(--surface);
    }}
    .plot-card-viewport {{
      width: 100%;
      height: 380px;
      position: relative;
      background: #000;
    }}
    .plot-card-frame {{
      width: 100%;
      height: 100%;
      border: none;
    }}
    .plot-card-footer {{
      padding: 0.6rem 1rem;
      background: var(--surface);
      border-top: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.72rem;
      color: var(--text-muted);
    }}
    @media (max-width: 900px) {{
      aside {{ width: 240px; }}
      #grid-view {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="logo-group">
      <div class="brand-badge">📈 BAROGRAPH HUB</div>
      <div class="project-title">{html.escape(project_name)}</div>
    </div>
    <div class="header-actions">
      <div class="status-pill">
        <span class="pulse-dot"></span>
        <span>Live Reload Active</span>
      </div>
      <div class="view-toggle">
        <button id="btn-view-stage" class="active" onclick="switchView('stage')">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18"/></svg>
          Stage Focus
        </button>
        <button id="btn-view-grid" onclick="switchView('grid')">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
          Grid Overview
        </button>
      </div>
    </div>
  </header>

  <div class="layout">
    <aside>
      <div class="sidebar-search">
        <input type="text" id="script-filter" class="search-input" placeholder="Search plot scripts..." oninput="filterScripts()" />
      </div>
      <div class="sidebar-list" id="sidebar-list">
        {sidebar_items_html}
      </div>
      <div class="sidebar-footer">
        <span>Discovered Plots: {len(scripts)}</span>
        <span style="font-family: monospace;">barograph serve</span>
      </div>
    </aside>

    <main>
      <!-- Stage Focus Mode -->
      <div id="stage-view">
        <div class="stage-toolbar">
          <div class="stage-title">
            <span id="stage-active-title">Loading...</span>
            <span id="stage-active-file" style="font-size: 0.75rem; color: var(--text-muted); font-family: monospace;"></span>
          </div>
          <div class="stage-actions">
            <button class="btn-icon" title="Reload Frame" onclick="reloadActiveFrame()">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
            </button>
            <a id="stage-raw-link" class="btn-icon" title="Open Standalone in New Tab" href="#" target="_blank">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/></svg>
            </a>
          </div>
        </div>
        <div class="stage-frame-container">
          <iframe id="main-stage-frame" class="stage-frame" src="/{default_active}"></iframe>
        </div>
      </div>

      <!-- Grid Overview Mode -->
      <div id="grid-view">
        {cards_html}
      </div>
    </main>
  </div>

  <script>
    const SCRIPTS = {scripts_json};
    let currentScript = "{default_active}";
    let currentView = "stage";

    function selectScript(relPath, forceStage = true) {{
      currentScript = relPath;
      const script = SCRIPTS.find(s => s.rel_path === relPath) || {{ title: relPath, name: relPath }};

      // Update sidebar active states
      document.querySelectorAll('.script-item').forEach(el => {{
        if (el.getAttribute('data-script') === relPath) {{
          el.classList.add('active');
        }} else {{
          el.classList.remove('active');
        }}
      }});

      // Update Stage View
      document.getElementById('stage-active-title').innerText = script.title;
      document.getElementById('stage-active-file').innerText = script.name;
      document.getElementById('stage-raw-link').href = '/' + relPath;
      const frame = document.getElementById('main-stage-frame');
      if (frame.getAttribute('src') !== '/' + relPath) {{
        frame.src = '/' + relPath;
      }}

      if (forceStage && currentView !== 'stage') {{
        switchView('stage');
      }}
    }}

    function switchView(mode) {{
      currentView = mode;
      const stageEl = document.getElementById('stage-view');
      const gridEl = document.getElementById('grid-view');
      const btnStage = document.getElementById('btn-view-stage');
      const btnGrid = document.getElementById('btn-view-grid');

      if (mode === 'stage') {{
        stageEl.style.display = 'flex';
        gridEl.style.display = 'none';
        btnStage.classList.add('active');
        btnGrid.classList.remove('active');
      }} else {{
        stageEl.style.display = 'none';
        gridEl.style.display = 'grid';
        btnStage.classList.remove('active');
        btnGrid.classList.add('active');
      }}
    }}

    function reloadActiveFrame() {{
      const frame = document.getElementById('main-stage-frame');
      if (frame) frame.src = frame.src;
    }}

    function filterScripts() {{
      const q = document.getElementById('script-filter').value.toLowerCase();
      document.querySelectorAll('.script-item').forEach(el => {{
        const text = el.innerText.toLowerCase();
        el.style.display = text.includes(q) ? 'flex' : 'none';
      }});
      document.querySelectorAll('.plot-card').forEach(el => {{
        const text = el.innerText.toLowerCase();
        el.style.display = text.includes(q) ? 'flex' : 'none';
      }});
    }}

    // Initialize first script selection
    if (SCRIPTS.length > 0) {{
      selectScript(SCRIPTS[0].rel_path, false);
    }}
  </script>
</body>
</html>
"""


class Dashboard:
    """Dashboard figure container compatible with Barograph protocol."""

    def __init__(self, project_name: str, base_dir: Path):
        self.project_name = project_name
        self.base_dir = base_dir
        self.scripts = discover_plot_scripts(base_dir)
        self._html = generate_dashboard_html(project_name, self.scripts)

    def to_html(self, *args: Any, **kwargs: Any) -> str:
        return self._html

    def _repr_html_(self) -> str:
        return self._html

    def write_html(self, file_or_path: Any, *args: Any, **kwargs: Any) -> None:
        if hasattr(file_or_path, "write"):
            file_or_path.write(self._html)
        else:
            with open(file_or_path, "w", encoding="utf-8") as f:
                f.write(self._html)


# Auto-detect workspace scripts and build Dashboard figure
dashboard = Dashboard(project_name=PROJECT_NAME, base_dir=PROJECT_DIR)
fig = dashboard


def plot() -> Dashboard:
    """Callable figure protocol hook."""
    return dashboard


def main() -> Dashboard:
    """Entrypoint when run directly or imported."""
    return dashboard


if __name__ == "__main__":
    try:
        from rich import print as rprint
    except ImportError:
        import re

        def rprint(*args, **kwargs):
            cleaned = [re.sub(r"\[/?[a-zA-Z0-9_\s=]+\]", "", str(a)) for a in args]
            print(*cleaned, **kwargs)

    rprint(f"[bold cyan]📈 Barograph Hub Dashboard Initialized for {PROJECT_NAME}[/bold cyan]")
    rprint(f"[dim]Discovered {len(dashboard.scripts)} plot script(s) in {PROJECT_DIR}[/dim]")
    for s in dashboard.scripts:
        rprint(f"  • [bold]{s.name}[/bold] -> [italic]{s.title}[/italic] ({s.size_kb:.1f} KB)")

    # If barograph binary is available, suggest or launch serve
    if shutil.which("barograph"):
        rprint("\n[bold green]Tip:[/bold green] Run [cyan]barograph serve[/cyan] for live preview and hot reload.")
    else:
        out_file = PROJECT_DIR / "index.html"
        dashboard.write_html(out_file)
        rprint(f"[green]Saved static dashboard preview to {out_file}[/green]")
