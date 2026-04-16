"""Value transformation support: apply simple transforms to CSV fields before diffing."""

from __future__ import annotations

from typing import Callable, Dict, List, Optional


class TransformError(Exception):
    pass


TRANSFORM_REGISTRY: Dict[str, Callable[[str], str]] = {
    "upper": str.upper,
    "lower": str.lower,
    "strip": str.strip,
    "title": str.title,
}


def parse_transforms(raw: Optional[str]) -> Optional[Dict[str, str]]:
    """Parse 'col:transform,col2:transform2' into a mapping."""
    if not raw:
        return None
    result: Dict[str, str] = {}
    for entry in raw.split(","):
        entry = entry.strip()
        if ":" not in entry:
            raise TransformError(f"Invalid transform spec {entry!r}: expected 'column:transform'")
        col, _, transform = entry.partition(":")
        col = col.strip()
        transform = transform.strip().lower()
        if not col:
            raise TransformError("Column name must not be empty")
        if transform not in TRANSFORM_REGISTRY:
            known = ", ".join(sorted(TRANSFORM_REGISTRY))
            raise TransformError(f"Unknown transform {transform!r}. Known: {known}")
        result[col] = transform
    return result


def validate_transforms(transforms: Dict[str, str], headers: List[str]) -> None:
    missing = [c for c in transforms if c not in headers]
    if missing:
        raise TransformError(f"Transform columns not in CSV headers: {missing}")


def apply_transforms(row: Dict[str, str], transforms: Dict[str, str]) -> Dict[str, str]:
    """Return a new row dict with transforms applied."""
    result = dict(row)
    for col, name in transforms.items():
        if col in result:
            fn = TRANSFORM_REGISTRY[name]
            result[col] = fn(result[col])
    return result


def transform_rows(
    rows: List[Dict[str, str]], transforms: Optional[Dict[str, str]]
) -> List[Dict[str, str]]:
    if not transforms:
        return rows
    return [apply_transforms(r, transforms) for r in rows]
