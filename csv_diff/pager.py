"""Pager support: optionally pipe output through a pager like `less`."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from typing import Optional

_DEFAULT_PAGER = "less -R"


class PagerError(Exception):
    """Raised when the pager process cannot be started."""


def _detect_pager() -> Optional[str]:
    """Return the pager command from the environment, or a sensible default."""
    pager = os.environ.get("CSV_DIFF_PAGER") or os.environ.get("PAGER")
    if pager:
        return pager
    if shutil.which("less"):
        return _DEFAULT_PAGER
    if shutil.which("more"):
        return "more"
    return None


def should_page(text: str, force: Optional[bool] = None) -> bool:
    """Decide whether paging is worthwhile.

    *force* overrides automatic detection when explicitly set to True/False.
    Otherwise paging is enabled when stdout is a TTY and the output is tall.
    """
    if force is not None:
        return force
    if not sys.stdout.isatty():
        return False
    terminal_lines = shutil.get_terminal_size(fallback=(80, 24)).lines
    return text.count("\n") >= terminal_lines


def page_output(text: str, pager_cmd: Optional[str] = None) -> None:
    """Write *text* through *pager_cmd* (or the auto-detected pager).

    Falls back to plain ``print`` when no pager is available or the subprocess
    cannot be launched.
    """
    cmd = pager_cmd or _detect_pager()
    if not cmd:
        print(text)
        return

    try:
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdin=subprocess.PIPE,
            encoding="utf-8",
            errors="replace",
        )
        proc.stdin.write(text)  # type: ignore[union-attr]
        proc.stdin.close()      # type: ignore[union-attr]
        proc.wait()
    except OSError as exc:
        raise PagerError(f"Could not launch pager '{cmd}': {exc}") from exc


def page_or_print(text: str, force: Optional[bool] = None, pager_cmd: Optional[str] = None) -> None:
    """Convenience wrapper that combines :func:`should_page` and :func:`page_output`.

    Checks whether paging is appropriate and either pipes *text* through the
    pager or falls back to a plain ``print``.  Callers that need fine-grained
    control should call :func:`should_page` and :func:`page_output` directly.

    Args:
        text: The output text to display.
        force: When ``True`` always page; when ``False`` never page; when
            ``None`` (default) the decision is made automatically.
        pager_cmd: Override the pager command.  Defaults to auto-detection.
    """
    if should_page(text, force=force):
        page_output(text, pager_cmd=pager_cmd)
    else:
        print(text)
