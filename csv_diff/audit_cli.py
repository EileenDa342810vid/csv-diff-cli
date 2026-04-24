"""CLI helpers for the --audit flag."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional, Sequence

from csv_diff.audit import AuditRecord, audit_diff, format_audit

DiffEvent = object  # avoid circular import at module level


def add_audit_arguments(parser: argparse.ArgumentParser) -> None:
    """Register --audit and --audit-run-id flags on *parser*."""
    parser.add_argument(
        "--audit",
        action="store_true",
        default=False,
        help="Print an audit trail of all diff events.",
    )
    parser.add_argument(
        "--audit-run-id",
        metavar="ID",
        default=None,
        help="Override the auto-generated run-id in the audit log.",
    )


def maybe_print_audit(
    args: argparse.Namespace,
    events: Sequence,
    key_column: str,
) -> bool:
    """If --audit is set, print the audit log and return True."""
    if not getattr(args, "audit", False):
        return False

    run_id: Optional[str] = getattr(args, "audit_run_id", None)
    try:
        records: List[AuditRecord] = audit_diff(
            events,  # type: ignore[arg-type]
            key_column=key_column,
            run_id=run_id,
        )
    except Exception as exc:  # pragma: no cover
        print(f"audit error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(format_audit(records))
    return True
