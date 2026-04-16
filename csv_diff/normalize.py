"""Value normalization transforms for CSV diff preprocessing."""

from __future__ import annotations

from typing import Callable, Dict, List, Optional


class NormalizeError(Exception):
    pass


_NORMALIZERS: Dict[str, Callable[[str], str]] = {
    "strip": str.strip,
    "lower": str.lower,
    "upper": str.upper,
    "nfc": lambda v: __import__("unicodedata").normalize("NFC", v),
}


def parse_normalizers(value: Optional[str]) -> Optional[List[str]]:
    """Parse a comma-separated list of normalizer names."""
    if not value or not value.strip():
        return None
    parts = [p.strip() for p in value.split(",")]
    for part in parts:
        if not part:
            raise NormalizeError("Empty normalizer entry in list.")
        if part not in _NORMALIZERS:
            raise NormalizeError(
                f"Unknown normalizer: {part!r}. "
                f"Valid options: {', '.join(sorted(_NORMALIZERS))}"
            )
    return parts


def apply_normalizers(value: str, names: List[str]) -> str:
    """Apply a sequence of normalizers to a single value."""
    for name in names:
        fn = _NORMALIZERS.get(name)
        if fn is None:
            raise NormalizeError(f"Unknown normalizer: {name!r}")
        value = fn(value)
    return value


def normalize_row(row: Dict[str, str], names: List[str]) -> Dict[str, str]:
    """Return a new row with all values normalized."""
    return {col: apply_normalizers(val, names) for col, val in row.items()}


def normalize_rows(
    rows: List[Dict[str, str]], names: Optional[List[str]]
) -> List[Dict[str, str]]:
    """Normalize all rows; return originals unchanged when names is None."""
    if not names:
        return rows
    return [normalize_row(row, names) for row in rows]
