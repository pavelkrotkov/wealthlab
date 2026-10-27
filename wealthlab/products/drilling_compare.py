"""Compare actual household cash/taxes with the same capital budget and a liquid-share policy."""

from wealthlab.household.projection import project
from wealthlab.products.drilling_reporting import annual_returns, total


def compare(scenario):
    if scenario.drilling_plan is None:
        raise ValueError("A drilling plan is required.")
    rows = {}
    for mode in ("drilling", "liquid_reference"):
        plan = scenario.drilling_plan.model_copy(update={"mode": mode})
        rows[mode] = project(scenario.model_copy(update={"drilling_plan": plan}))
    return dict(
        input=scenario.model_dump(mode="json"),
        rows=rows,
        outcomes={key: outcome(value) for key, value in rows.items()},
        full_tax_optimization_supported=False,
        scope="Conditional supplied tax facts; no legal eligibility or full-tax certificate",
    )


def outcome(rows):
    final = rows[-1]
    tax = sum(r["total_liability"] for r in annual_returns(rows).values())
    return dict(
        conditional_after_tax_net_wealth=final["net_wealth"],
        closing_cash=final["closing_cash"],
        unpaid_tax_position=final.get("tax_position", 0),
        product_value=final["drilling_account_value"],
        recourse_liability=final["drilling_recourse_liability"],
        call_funded=total(rows, "drilling_call_funded"),
        recourse_funded=total(rows, "drilling_recourse_funded"),
        distributions=sum(r["drilling_distribution"] + r["drilling_exit_cash"] for r in rows),
        actual_annual_tax_liability=tax,
        spending_tax_failure_months=sum(r["funding_failure"] for r in rows),
        product_failure_months=sum(r["drilling_product_failure"] for r in rows),
        joint_funding_feasible=not any(
            r["funding_failure"] or r["drilling_product_failure"] for r in rows
        ),
    )
