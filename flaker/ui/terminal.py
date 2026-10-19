"""Terminal raw mode handling, ANSI stripping, and column fitting for Flaker."""

import os
import re
import select
import sys
import termios
import tty
from typing import Any, Sequence

ANSI_REGEX = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")


def strip_ansi(text: str) -> str:
    """Strips ANSI escape codes to measure true visual character length."""
    return ANSI_REGEX.sub("", text)


def read_key() -> str:
    """
    Reads a single raw keypress or ANSI escape sequence directly from stdin.
    Uses os.read() without TextIOWrapper buffering to ensure escape sequences
    arrive atomically and reliably in modern terminal emulators.
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        raw = os.read(fd, 32)
        if not raw:
            return "ctrl_d"

        # Check if this is an escape sequence
        if raw == b"\x1b":
            # Check if more bytes are pending in the kernel pty buffer
            r, _, _ = select.select([fd], [], [], 0.025)
            if r:
                raw += os.read(fd, 32)
            else:
                return "esc"

        # Arrow keys & cursor navigation:
        if raw.startswith(b"\x1b") and raw.endswith(b"A"):
            return "up"
        if raw.startswith(b"\x1b") and raw.endswith(b"B"):
            return "down"
        if raw.startswith(b"\x1b") and raw.endswith(b"C"):
            return "right"
        if raw.startswith(b"\x1b") and raw.endswith(b"D"):
            return "left"

        # Enter, space, vim navigation, controls
        if raw in (b"\r", b"\n"):
            return "enter"
        if raw == b" ":
            return "space"
        if raw == b"\x03":  # Ctrl+C
            return "ctrl_c"
        if raw == b"\x04":  # Ctrl+D
            return "ctrl_d"
        if raw in (b"k", b"K"):
            return "up"
        if raw in (b"j", b"J"):
            return "down"
        if raw in (b"a", b"A"):
            return "a"
        if raw in (b"q", b"Q"):
            return "q"

        return raw.decode("utf-8", errors="ignore")
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def fit_line(
    prefix: str, label_styled: str, label_plain: str, desc: str, max_w: int
) -> str:
    """
    Ensures a menu item line never exceeds max_w visual columns.
    Prevents terminal wrapping so cursor up/down operations remain 100% in sync.
    """
    prefix_len = len(strip_ansi(prefix))
    avail = max_w - prefix_len
    if avail <= 5:
        return prefix + label_plain[: max(0, avail)]

    if not desc:
        if len(label_plain) <= avail:
            return f"{prefix}{label_styled}"
        return f"{prefix}{label_plain[: max(0, avail - 3)]}..."

    # Both label and desc present
    if len(label_plain) + 2 + len(desc) <= avail:
        return f"{prefix}{label_styled} \033[90m{desc}\033[0m"

    # Fit label and truncated description
    if len(label_plain) + 6 <= avail:
        rem = avail - len(label_plain) - 4
        trunc_desc = desc[: max(0, rem)] + "..."
        return f"{prefix}{label_styled} \033[90m{trunc_desc}\033[0m"

    # Narrow terminal: label only
    if len(label_plain) <= avail:
        return f"{prefix}{label_styled}"
    return f"{prefix}{label_plain[: max(0, avail - 3)]}..."


def normalize_options(options: Sequence[Any]) -> list[tuple[str, str, str]]:
    """
    Normalizes option entries into (key, label, description).
    Accepts:
      - "name" -> (name, name, "")
      - ("key", "label") -> (key, label, "")
      - ("key", "label", "description") -> (key, label, description)
    """
    result = []
    for opt in options:
        if isinstance(opt, (list, tuple)):
            if len(opt) == 1:
                result.append((str(opt[0]), str(opt[0]), ""))
            elif len(opt) == 2:
                result.append((str(opt[0]), str(opt[1]), ""))
            else:
                result.append((str(opt[0]), str(opt[1]), str(opt[2])))
        else:
            result.append((str(opt), str(opt), ""))
    return result
