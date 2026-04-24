"""Track high-water-mark (maximum observed change count) across runs."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class WatermarkError(Exception):  # noqa: N818
    pass


@dataclass
class Watermark:
    path: Path
    previous: int
    current: int

    @property
    def is_new_high(self) -> bool:
        return self.current > self.previous


def parse_watermark_path(value: Optional[str]) -> Optional[Path]:
    """Return a Path or None when *value* is empty/None."""
    if not value:
        return None
    return Path(value)


def load_watermark(path: Path) -> int:
    """Return the stored count, or 0 if the file does not yet exist."""
    if not path.exists():
        return 0
    try:
        data = json.loads(path.read_text())
        return int(data["high"])
    except (KeyError, ValueError, json.JSONDecodeError) as exc:
        raise WatermarkError(f"Cannot read watermark file {path}: {exc}") from exc


def save_watermark(path: Path, count: int) -> None:
    """Persist *count* to *path* (overwrites unconditionally)."""
    path.write_text(json.dumps({"high": count}))


def check_watermark(path: Path, current: int) -> Watermark:
    """Load the previous high, update if *current* exceeds it, return summary."""
    previous = load_watermark(path)
    if current > previous:
        save_watermark(path, current)
    return Watermark(path=path, previous=previous, current=current)


def format_watermark(wm: Watermark) -> str:
    lines = [
        f"Watermark : {wm.path}",
        f"Previous  : {wm.previous}",
        f"Current   : {wm.current}",
    ]
    if wm.is_new_high:
        lines.append("Status    : NEW HIGH")
    else:
        lines.append("Status    : within previous high")
    return "\n".join(lines)
