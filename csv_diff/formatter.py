"""Human-readable formatting for CSV diff results."""

from csv_diff.diff import DiffResult, RowAdded, RowModified, RowRemoved

ADD_COLOR = "\033[32m"
REMOVE_COLOR = "\033[31m"
MODIFY_COLOR = "\033[33m"
RESET = "\033[0m"
BOLD = "\033[1m"


def _format_row(row: dict[str, str], prefix: str, color: str, highlight: set[str] | None = None) -> list[str]:
    lines = []
    for col, val in row.items():
        marker = "*" if highlight and col in highlight else " "
        lines.append(f"{color}{prefix} {marker} {col}: {val}{RESET}")
    return lines


def format_diff(results: DiffResult, use_color: bool = True) -> str:
    """Render diff results as a human-readable string.

    Args:
        results: Output from :func:`csv_diff.diff.diff_csv`.
        use_color: Whether to include ANSI color codes.

    Returns:
        A formatted multi-line string describing all changes.
    """
    if not results:
        return "No differences found."

    c_add = ADD_COLOR if use_color else ""
    c_rem = REMOVE_COLOR if use_color else ""
    c_mod = MODIFY_COLOR if use_color else ""
    reset = RESET if use_color else ""
    bold = BOLD if use_color else ""

    lines: list[str] = []

    for event in results:
        if isinstance(event, RowAdded):
            lines.append(f"{bold}{c_add}+ Added row (key={event.key}){reset}")
            lines.extend(_format_row(event.row, "+", c_add) if use_color else _format_row(event.row, "+", ""))
        elif isinstance(event, RowRemoved):
            lines.append(f"{bold}{c_rem}- Removed row (key={event.key}){reset}")
            lines.extend(_format_row(event.row, "-", c_rem) if use_color else _format_row(event.row, "-", ""))
        elif isinstance(event, RowModified):
            changed_set = set(event.changed_columns)
            lines.append(f"{bold}{c_mod}~ Modified row (key={event.key}){reset}")
            lines.append(f"{c_mod}  Changed columns: {', '.join(event.changed_columns)}{reset}")
            lines.extend(_format_row(event.old_row, "-", c_rem, highlight=changed_set))
            lines.extend(_format_row(event.new_row, "+", c_add, highlight=changed_set))
        lines.append("")

    return "\n".join(lines).rstrip()
