"""Unfilled optional Roth requests and taxable recognition are separate from spending success."""

from decimal import Decimal

ZERO = Decimal(0)


def summary(rows):
    audit = rows[-1].get("workplace_roth_audit", [])
    if not audit:
        return {}
    failed = [r for r in audit if r["unfilled"]]
    return dict(
        workplace_roth_gross_cash_total=total(audit, "gross"),
        workplace_roth_unfilled_total=total(audit, "unfilled"),
        workplace_roth_taxable_federal_total=total(audit, "federal_taxable"),
        workplace_roth_taxable_nj_conditional_total=total(audit, "nj_taxable"),
        first_unfilled_workplace_roth=failed[0]["date"] if failed else None,
    )


def total(rows, key):
    return sum((r[key] for r in rows), ZERO)
