"""Terminal UI, ANSI styling, and interactive menu engine for Flaker."""

import os
import shutil
import sys
from contextlib import contextmanager
from typing import Any, Iterator, Sequence

from flaker.ui.spinner import Spinner
from flaker.ui.terminal import fit_line, normalize_options, read_key, strip_ansi


class UI:
    """Terminal styling, panels, banners, and interactive menus."""

    def __init__(
        self, app_name: str = "flaker", icon: str = "❄️", badge_color: str = "1;34"
    ):
        self.app_name = app_name
        self.icon = icon
        self.badge_color = badge_color
        self._color_mode = "auto"

    def set_color_mode(self, mode: str) -> None:
        self._color_mode = mode.lower()

    @property
    def use_color(self) -> bool:
        if self._color_mode == "never":
            return False
        if self._color_mode == "always":
            return True
        if "NO_COLOR" in os.environ:
            return False
        if os.environ.get("CLICOLOR_FORCE", "0") != "0" or "FORCE_COLOR" in os.environ:
            return True
        return sys.stdout.isatty() or os.environ.get("COLORTERM") in (
            "truecolor",
            "24bit",
        )

    def style(self, text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self.use_color else text

    def bold(self, text: str) -> str:
        return self.style(text, "1")

    def dim(self, text: str) -> str:
        return self.style(text, "90")

    def blue(self, text: str) -> str:
        return self.style(text, "1;34")

    def cyan(self, text: str) -> str:
        return self.style(text, "0;36")

    def bold_cyan(self, text: str) -> str:
        return self.style(text, "1;36")

    def green(self, text: str) -> str:
        return self.style(text, "0;32")

    def bold_green(self, text: str) -> str:
        return self.style(text, "1;32")

    def yellow(self, text: str) -> str:
        return self.style(text, "1;33")

    def red(self, text: str) -> str:
        return self.style(text, "1;31")

    def magenta(self, text: str) -> str:
        return self.style(text, "1;35")

    def badge(self) -> str:
        return self.style(f"{self.icon} [{self.app_name}]", self.badge_color)

    def status(self, symbol: str, message: str, code: str = "1") -> str:
        return f"{self.badge()} {self.style(f'{symbol} {message}', code)}"

    def success(self, msg: str) -> None:
        print(self.status("✔", msg, "1;32"))

    def info(self, msg: str, symbol: str = "ℹ️") -> None:
        print(self.status(symbol, msg, "1;34"))

    def warn(self, msg: str) -> None:
        print(self.status("⚠️", msg, "1;33"))

    def error(self, msg: str) -> None:
        print(self.status("✘", msg, "1;31"), file=sys.stderr)

    def action(self, msg: str, symbol: str = "⚡") -> None:
        print(self.status(symbol, msg, "0;36"))

    def prompt(self, message: str, default: str = "") -> str:
        """Prompts user for text input with styled badge and default value."""
        suffix = f" {self.dim(f'[{default}]')}: " if default else ": "
        prompt_str = f"{self.badge()} {self.bold(message)}{suffix}"
        try:
            val = input(prompt_str).strip()
            return val if val else default
        except (KeyboardInterrupt, EOFError):
            print()
            sys.exit(0)

    def confirm(self, message: str, default: bool = False) -> bool:
        """Prompts user for a yes/no confirmation with styled badge."""
        choices = "Y/n" if default else "y/N"
        suffix = f" {self.dim(f'[{choices}]')}: "
        prompt_str = f"{self.badge()} {self.bold(message)}{suffix}"
        try:
            val = input(prompt_str).strip().lower()
            if not val:
                return default
            return val in ("y", "yes")
        except (KeyboardInterrupt, EOFError):
            print()
            sys.exit(0)

    def header(self, title: str, width: int = 76) -> None:
        border = self.blue("=" * width)
        print(f"\n{border}\n {self.bold(title)}\n{border}")

    def subheader(self, title: str, width: int = 76) -> None:
        rule_part = self.dim("-" * max(0, width - len(title) - 5))
        print(f"\n{self.cyan(f'--- {title}')} {rule_part}")

    def panel(
        self,
        title: str,
        lines: Sequence[str] | str,
        border_color: str = "0;36",
        width: int = 76,
        stream: Any = None,
    ) -> None:
        """Renders a width-aware rounded box panel (╭─╮│╰─╯)."""
        out = stream or sys.stdout
        body_lines = lines.splitlines() if isinstance(lines, str) else list(lines)

        term_cols = shutil.get_terminal_size(fallback=(80, 24)).columns
        box_w = min(width, max(36, term_cols - 2))
        inner_w = box_w - 4

        title_clean = strip_ansi(title)
        title_segment = f" {title} " if title else ""
        top_fill = max(1, box_w - 3 - len(title_clean) - (2 if title else 0))
        top_border = (
            self.style("╭─", border_color)
            + (self.bold(title_segment) if title else "")
            + self.style("─" * top_fill + "╮", border_color)
        )
        bottom_border = self.style("╰" + "─" * (box_w - 2) + "╯", border_color)
        side = self.style("│", border_color)

        print(top_border, file=out)
        for raw_line in body_lines:
            vis_len = len(strip_ansi(raw_line))
            if vis_len <= inner_w:
                pad = " " * (inner_w - vis_len)
                print(f"{side} {raw_line}{pad} {side}", file=out)
            else:
                plain = strip_ansi(raw_line)
                clipped = plain[: max(0, inner_w - 3)] + "..."
                pad = " " * max(0, inner_w - len(clipped))
                print(f"{side} {clipped}{pad} {side}", file=out)
        print(bottom_border, file=out)

    def error_panel(self, title: str, lines: Sequence[str] | str) -> None:
        """Renders a formatted error diagnostic panel to stderr."""
        styled_title = self.red(f"✘ {title}")
        self.panel(styled_title, lines, border_color="1;31", stream=sys.stderr)

    @contextmanager
    def spinner(self, message: str) -> Iterator[Spinner]:
        """Context manager for zero-dependency braille console spinners."""
        sp = Spinner(self, message)
        sp.start()
        try:
            yield sp
        except Exception:
            sp.stop()
            raise
        else:
            sp.stop()

    def select(
        self,
        title: str,
        options: Sequence[Any],
        default_index: int = 0,
    ) -> str:
        """
        Single-select interactive menu with arrow key navigation.
        Width & height aware: truncates wide lines and paginates lists to fit any terminal size.
        """
        items = normalize_options(options)
        if not items:
            return ""

        # Fallback for non-interactive / non-TTY
        if not sys.stdin.isatty():
            print(f"\n{self.badge()} {self.bold(title)}")
            for idx, (k, lbl, desc) in enumerate(items, 1):
                extra = f" - {desc}" if desc else ""
                print(f"  [{idx}] {lbl}{extra}")
            ans = input("Choice [1]: ").strip()
            if ans.isdigit() and 1 <= int(ans) <= len(items):
                return items[int(ans) - 1][0]
            return items[0][0]

        current = max(0, min(default_index, len(items) - 1))
        scroll_offset = 0
        rendered_lines = 0

        # Hide cursor
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

        try:
            while True:
                term_size = shutil.get_terminal_size(fallback=(80, 24))
                cols, term_rows = term_size.columns, term_size.lines
                max_w = max(25, cols - 1)

                max_visible = max(3, min(len(items), term_rows - 5, 10))

                if current < scroll_offset:
                    scroll_offset = current
                elif current >= scroll_offset + max_visible:
                    scroll_offset = current - max_visible + 1
                scroll_offset = max(
                    0, min(scroll_offset, max(0, len(items) - max_visible))
                )

                lines = []
                raw_title = f"{self.badge()} {self.bold(title)}"
                lines.append(
                    raw_title
                    if len(strip_ansi(raw_title)) <= max_w
                    else raw_title[:max_w]
                )

                raw_help = self.dim(
                    "  (Use ↑/↓ or j/k to navigate, Enter to select, q/Ctrl+C to cancel)"
                )
                lines.append(
                    raw_help
                    if len(strip_ansi(raw_help)) <= max_w
                    else self.dim("  (↑/↓: navigate, Enter: select)")
                )
                lines.append("")

                if scroll_offset > 0:
                    lines.append(self.dim(f"  ▲ ({scroll_offset} more above...)"))

                visible_items = items[scroll_offset : scroll_offset + max_visible]
                for idx_offset, (key, label, desc) in enumerate(visible_items):
                    actual_idx = scroll_offset + idx_offset
                    if actual_idx == current:
                        pointer = self.bold_cyan("❯")
                        styled_lbl = self.bold_cyan(label)
                    else:
                        pointer = " "
                        styled_lbl = label

                    prefix = f"  {pointer} "
                    lines.append(fit_line(prefix, styled_lbl, label, desc, max_w))

                if scroll_offset + max_visible < len(items):
                    remaining = len(items) - (scroll_offset + max_visible)
                    lines.append(self.dim(f"  ▼ ({remaining} more below...)"))

                if rendered_lines > 0:
                    sys.stdout.write(f"\033[{rendered_lines}A\r")
                for line in lines:
                    sys.stdout.write(f"\033[2K{line}\r\n")
                sys.stdout.flush()
                rendered_lines = len(lines)

                key = read_key()
                if key == "up":
                    current = (current - 1) % len(items)
                elif key == "down":
                    current = (current + 1) % len(items)
                elif key == "enter":
                    break
                elif key in ("ctrl_c", "ctrl_d", "q", "esc"):
                    if rendered_lines > 0:
                        sys.stdout.write(f"\033[{rendered_lines}A\r")
                        for _ in range(rendered_lines):
                            sys.stdout.write("\033[2K\r\n")
                        sys.stdout.write(f"\033[{rendered_lines}A\r")
                        sys.stdout.flush()
                    print("\nAborted.")
                    sys.exit(0)

            sys.stdout.write(f"\033[{rendered_lines}A\r")
            for _ in range(rendered_lines):
                sys.stdout.write("\033[2K\r\n")
            sys.stdout.write(f"\033[{rendered_lines}A\r")
            print(
                f"{self.badge()} {self.dim(title)} {self.bold_green(items[current][1])}"
            )
            sys.stdout.flush()
            return items[current][0]
        finally:
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()

    def multiselect(
        self,
        title: str,
        options: Sequence[Any],
        preselected: Sequence[str] | set[str] | None = None,
    ) -> list[str]:
        """
        Multi-select interactive menu with arrow key navigation and spacebar toggling.
        Width & height aware: truncates wide lines and paginates lists to fit any terminal size.
        """
        items = normalize_options(options)
        if not items:
            return []

        selected_keys: set[str] = set(preselected) if preselected else set()

        if not sys.stdin.isatty():
            print(f"\n{self.badge()} {self.bold(title)}")
            for idx, (k, lbl, desc) in enumerate(items, 1):
                mark = "[*]" if k in selected_keys else "[ ]"
                extra = f" - {desc}" if desc else ""
                print(f"  {mark} [{idx}] {lbl}{extra}")
            ans = input("Select numbers (comma/space separated): ").strip()
            chosen = []
            for tok in ans.replace(",", " ").split():
                if tok.isdigit() and 1 <= int(tok) <= len(items):
                    chosen.append(items[int(tok) - 1][0])
            return chosen if chosen else list(selected_keys)

        current = 0
        scroll_offset = 0
        rendered_lines = 0

        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

        try:
            while True:
                term_size = shutil.get_terminal_size(fallback=(80, 24))
                cols, term_rows = term_size.columns, term_size.lines
                max_w = max(25, cols - 1)

                max_visible = max(3, min(len(items), term_rows - 5, 10))

                if current < scroll_offset:
                    scroll_offset = current
                elif current >= scroll_offset + max_visible:
                    scroll_offset = current - max_visible + 1
                scroll_offset = max(
                    0, min(scroll_offset, max(0, len(items) - max_visible))
                )

                lines = []
                raw_title = f"{self.badge()} {self.bold(title)}"
                lines.append(
                    raw_title
                    if len(strip_ansi(raw_title)) <= max_w
                    else raw_title[:max_w]
                )

                raw_help = self.dim(
                    "  (↑/↓: navigate, Space: toggle, a: all, Enter: confirm, q/Ctrl+C: cancel)"
                )
                lines.append(
                    raw_help
                    if len(strip_ansi(raw_help)) <= max_w
                    else self.dim("  (↑/↓: nav, Space: toggle, Enter: ok)")
                )
                lines.append("")

                if scroll_offset > 0:
                    lines.append(self.dim(f"  ▲ ({scroll_offset} more above...)"))

                visible_items = items[scroll_offset : scroll_offset + max_visible]
                for idx_offset, (key, label, desc) in enumerate(visible_items):
                    actual_idx = scroll_offset + idx_offset
                    is_checked = key in selected_keys
                    check = self.bold_green("[✔]") if is_checked else self.dim("[ ]")

                    if actual_idx == current:
                        pointer = self.bold_cyan("❯")
                        styled_lbl = (
                            self.bold_cyan(label) if is_checked else self.bold(label)
                        )
                    else:
                        pointer = " "
                        styled_lbl = self.green(label) if is_checked else label

                    prefix = f"  {pointer} {check} "
                    lines.append(fit_line(prefix, styled_lbl, label, desc, max_w))

                if scroll_offset + max_visible < len(items):
                    remaining = len(items) - (scroll_offset + max_visible)
                    lines.append(self.dim(f"  ▼ ({remaining} more below...)"))

                if rendered_lines > 0:
                    sys.stdout.write(f"\033[{rendered_lines}A\r")
                for line in lines:
                    sys.stdout.write(f"\033[2K{line}\r\n")
                sys.stdout.flush()
                rendered_lines = len(lines)

                key = read_key()
                if key == "up":
                    current = (current - 1) % len(items)
                elif key == "down":
                    current = (current + 1) % len(items)
                elif key == "space":
                    cur_key = items[current][0]
                    if cur_key in selected_keys:
                        selected_keys.remove(cur_key)
                    else:
                        selected_keys.add(cur_key)
                elif key == "a":
                    if len(selected_keys) == len(items):
                        selected_keys.clear()
                    else:
                        selected_keys = {k for k, _, _ in items}
                elif key == "enter":
                    break
                elif key in ("ctrl_c", "ctrl_d", "q", "esc"):
                    if rendered_lines > 0:
                        sys.stdout.write(f"\033[{rendered_lines}A\r")
                        for _ in range(rendered_lines):
                            sys.stdout.write("\033[2K\r\n")
                        sys.stdout.write(f"\033[{rendered_lines}A\r")
                        sys.stdout.flush()
                    print("\nAborted.")
                    sys.exit(0)

            sys.stdout.write(f"\033[{rendered_lines}A\r")
            for _ in range(rendered_lines):
                sys.stdout.write("\033[2K\r\n")
            sys.stdout.write(f"\033[{rendered_lines}A\r")
            chosen_labels = [lbl for k, lbl, _ in items if k in selected_keys]
            print(
                f"{self.badge()} {self.dim(title)} {self.bold_green(', '.join(chosen_labels) if chosen_labels else 'none')}"
            )
            sys.stdout.flush()
            return [k for k, _, _ in items if k in selected_keys]
        finally:
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()
