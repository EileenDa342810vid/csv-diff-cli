"""ANSI colour helpers for diff output."""

from __future__ import annotations

import os
import sys

_RESET = "\033[0m"
_BOLD = "\033[1m"

_CODES: dict[str, str] = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bold": _BOLD,
}


def _colour_enabled(force: bool | None = None) -> bool:
    """Return True when ANSI colour should be emitted.

    Respects *NO_COLOR* env var (https://no-color.org/) and whether stdout is
    a TTY.  *force* overrides both checks when not None.
    """
    if force is not None:
        return force
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def colorize(text: str, colour: str, *, force: bool | None = None) -> str:
    """Wrap *text* in ANSI escape codes for *colour*.

    Returns *text* unchanged when colour is disabled.
    """
    if not _colour_enabled(force):
        return text
    code = _CODES.get(colour, "")
    if not code:
        return text
    return f"{code}{text}{_RESET}"


def added(text: str, *, force: bool | None = None) -> str:
    """Format text as an added line (green)."""
    return colorize(text, "green", force=force)


def removed(text: str, *, force: bool | None = None) -> str:
    """Format text as a removed line (red)."""
    return colorize(text, "red", force=force)


def modified(text: str, *, force: bool | None = None) -> str:
    """Format text as a modified line (yellow)."""
    return colorize(text, "yellow", force=force)


def header(text: str, *, force: bool | None = None) -> str:
    """Format text as a section header (bold cyan)."""
    if not _colour_enabled(force):
        return text
    return f"{_BOLD}{_CODES['cyan']}{text}{_RESET}"
