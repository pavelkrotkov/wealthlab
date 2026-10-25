"""Cash funding and product constraints have separate outcomes and a joint feasibility result."""

from decimal import Decimal

from wealthlab.markets.option_reporting import outcome as option_outcome
from wealthlab.markets.rollover_report import summary as rollover_summary
from wealthlab.markets.roth_cash_report import summary as roth_cash_summary
from wealthlab.markets.workplace_rmd_report import summary as rmd_summary
from wealthlab.tax.payments import missed_schedule


def funding(rows):
    failures = [r for r in rows if r["funding_failure"]]
    return dict(
        funded=not failures,
        discretionary_spending_reduction=sum(
            (r.get("guardrail_discretionary_reduction", 0) for r in rows), Decimal(0)
        ),
        first_failure=failures[0]["date"] if failures else None,
        funding_shortfall=sum((r["funding_shortfall"] for r in rows), Decimal(0)),
        missed_tax_schedule_months=sum(missed_schedule(r) for r in rows),
        **product_outcome(rows, not failures),
        **rmd_summary(rows),
        **rollover_summary(rows),
        **roth_cash_summary(rows),
        cash_reserve_breach_months=sum(r["closing_cash"] < r["reserve_target"] for r in rows),
    )


def product_outcome(rows, funded):
    return option_outcome(rows, funded)


def product_totals(results):
    feasible = sum(r["product_feasible"] for r in results)
    joint = sum(r["joint_feasible"] for r in results)
    return dict(
        product_feasible_paths=feasible,
        joint_feasible_paths=joint,
        joint_feasibility_fraction=joint / len(results),
    )
