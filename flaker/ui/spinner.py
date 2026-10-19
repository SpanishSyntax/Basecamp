"""Zero-dependency braille terminal spinner for background operations."""

import sys
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flaker.ui.engine import UI


class Spinner:
    """Zero-dependency braille terminal spinner for background operations."""

    FRAMES = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")

    def __init__(self, ui_instance: "UI", message: str):
        self.ui = ui_instance
        self.message = message
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._is_tty = sys.stdout.isatty()

    def update(self, message: str) -> None:
        """Updates the active spinner status text."""
        self.message = message

    def _spin(self) -> None:
        idx = 0
        while not self._stop_event.is_set():
            frame = self.ui.bold_cyan(self.FRAMES[idx % len(self.FRAMES)])
            line = f"\r\033[2K{self.ui.badge()} {frame} {self.message}"
            sys.stdout.write(line)
            sys.stdout.flush()
            idx += 1
            self._stop_event.wait(0.08)

    def start(self) -> None:
        if not self._is_tty:
            self.ui.action(self.message, symbol="⏳")
            return
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def stop(self, final_message: str | None = None, ok: bool = True) -> None:
        if not self._is_tty:
            if final_message:
                if ok:
                    self.ui.success(final_message)
                else:
                    self.ui.error(final_message)
            return

        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.5)
        sys.stdout.write("\r\033[2K\033[?25h")
        sys.stdout.flush()
        if final_message:
            if ok:
                self.ui.success(final_message)
            else:
                self.ui.error(final_message)
