"""Preserve existing federal output names while giving NJ an independent matching ledger."""


def key(jurisdiction, field):
    if jurisdiction == "federal" and field in {"matches", "unmatched_quantity"}:
        return "wash_" + field
    return jurisdiction + "_wash_" + field
