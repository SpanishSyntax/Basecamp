"""Terminal UI, ANSI styling, and interactive menu engine for Flaker."""

from flaker.ui.engine import UI
from flaker.ui.spinner import Spinner
from flaker.ui.terminal import strip_ansi

ui = UI()

__all__ = ["UI", "ui", "Spinner", "strip_ansi"]
