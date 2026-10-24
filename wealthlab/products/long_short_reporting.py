"""Classify resolved margin actions separately from unresolved product constraints."""

from collections import Counter


def any_stage(row, name):
    return any(row.get(f"{prefix}{name}", 0) for prefix in ("entry_", "", "post_trade_"))


def classify(row):
    flags = dict(
        margin_triggered=bool(any_stage(row, "margin_requested")),
        margin_unresolved=bool(any_stage(row, "margin_exit_blocked")),
        negative_equity=row["equity"] < 0,
        exit_blocked=row.get("terminal_exit_blocked", False),
    )
    flags["constraints_failed"] = any(flags[k] for k in flags if k != "margin_triggered")
    return flags


def class_counts(rows):
    return Counter(k for row in rows for k, value in classify(row).items() if value)
