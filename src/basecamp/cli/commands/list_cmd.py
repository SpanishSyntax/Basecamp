"""Handler for 'basecamp list' command."""

import shutil

from basecamp.core.models import Role
from basecamp.ui import ui


def display_roles_list(roles_db: dict[str, Role], aliases: dict[str, str]) -> None:
    """Prints a clean, formatted terminal table of all registered roles inside a ui.panel."""
    if ui.is_json:
        data = [
            {
                "role": r_key,
                "category": roles_db[r_key].category,
                "description": roles_db[r_key].description,
                "aliases": [a for a, target in aliases.items() if target == r_key],
            }
            for r_key in sorted(roles_db.keys())
        ]
        ui.json({"status": "ok", "count": len(data), "roles": data})
        return

    categories: dict[str, list[str]] = {}
    for r_key, role in roles_db.items():
        categories.setdefault(role.category, []).append(r_key)

    term_cols = shutil.get_terminal_size(fallback=(88, 24)).columns
    box_w = min(88, max(36, term_cols - 2))
    inner_w = box_w - 4

    hdr_role = ui.bold(f"{'ROLE':<10}")
    hdr_cat = ui.bold(f"{'CATEGORY':<18}")
    hdr_desc = ui.bold("DESCRIPTION")
    sep_line = ui.dim("─" * inner_w)

    panel_lines: list[str] = [
        f"{hdr_role}  {hdr_cat}  {hdr_desc}",
        sep_line,
    ]

    for cat in sorted(categories.keys()):
        for r_key in sorted(categories[cat]):
            role = roles_db[r_key]
            r_col = ui.cyan(f"{r_key:<10}")
            cat_col = f"{role.category:<18}"
            panel_lines.append(f"{r_col}  {cat_col}  {role.description}")

    ui.panel("Basecamp Roles Registry", panel_lines, width=box_w)
    if not ui.is_agent:
        ui.info(
            f"Run '{ui.bold('basecamp info <role>')}' for packages, hooks, and starter files.\n",
            symbol="💡",
        )
