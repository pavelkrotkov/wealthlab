"""Optional rollover requests are reported separately from mandatory spending failures."""

from decimal import Decimal

ZERO = Decimal(0)


def summary(rows):
    audit = rows[-1].get("workplace_rollover_audit", [])
    if not audit:
        return {}
    blocked = [r for r in audit if r["unfilled"]]
    return dict(
        workplace_rollover_funded_total=sum((r["funded"] for r in audit), ZERO),
        workplace_rollover_unfilled_total=sum((r["unfilled"] for r in audit), ZERO),
        first_unfilled_workplace_rollover=blocked[0]["date"] if blocked else None,
    )
