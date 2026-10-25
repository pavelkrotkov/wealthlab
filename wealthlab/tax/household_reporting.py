"""Latest annual recognition and actual dated cash payments are different measurements.

January/terminal wash revisions supersede the original annual liability but
do not rewrite the original cash history. Partial annual records are accrued
recognition, not a complete return; unresolved provisional years remain visible.
"""

from decimal import Decimal

ZERO = Decimal(0)


def annual_results(rows):
    annual = {row["date"][:4]: row["annual_tax"] for row in rows}
    annual.update({str(r["year"]): r["final_result"] for r in revisions(rows)})
    return annual


def revisions(rows):
    return rows[-1].get("lot_audit", {}).get("return_reconciliations", [])


def summary(rows):
    annual = annual_results(rows)
    revised = {str(r["year"]) for r in revisions(rows)}
    provisional = {r["date"][:4] for r in rows if r.get("tax_return_provisional")}
    cash = sum((paid(r) for r in rows), ZERO)
    refunds = sum((r["tax_refund_received"] for r in rows), ZERO)
    return dict(
        reported_tax_liability=sum((r["total_liability"] for r in annual.values()), ZERO),
        reported_employee_payroll=sum(
            (r["federal"]["employee_payroll"] for r in annual.values()), ZERO
        ),
        gross_cash_taxes_paid=cash,
        cash_tax_refunds_received=refunds,
        net_cash_taxes_paid=cash - refunds,
        provisional_tax_years=sorted(provisional - revised),
        partial_tax_years=partial_years(rows),
    )


def paid(row):
    return sum(
        (
            row.get(key, ZERO)
            for key in (
                "tax_withheld",
                "tax_source_withholding",
                "tax_estimates_paid",
                "tax_settlement_paid",
                "prior_tax_paid",
            )
        ),
        ZERO,
    )


def partial_years(rows):
    latest = {r["date"][:4]: r["period_end"] for r in rows}
    return sorted(year for year, end in latest.items() if end != f"{int(year) + 1}-01-01")
