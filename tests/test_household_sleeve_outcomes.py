"""A resolved margin action can preserve spending and joint product feasibility."""

from household_sleeve_cases import change, flat

from wealthlab.household.projection import project
from wealthlab.markets.household_outcomes import funding, product_totals


def test_configured_positive_equity_liquidation_funds_spending_without_constraint_failure():
    def configure(data):
        sleeve = data["sleeve_plan"]["sleeves"][0]
        sleeve["case"]["maintenance_fraction_of_gross"] = "0.6"
        sleeve["observations"][0]["short_return"] = "1"
        data["expenses"] = [
            dict(
                id="living",
                provenance="assumption",
                start="2026-01-01",
                end="2027-01-01",
                monthly_amount=2000,
                currency="USD",
                annual_growth=0,
                category="essential",
            )
        ]

    rows = project(change(flat(), configure))
    outcome = funding(rows)
    assert rows[-1]["closing_cash"] == 56000
    assert (outcome["funded"], outcome["product_feasible"], outcome["joint_feasible"]) == (
        True,
        True,
        True,
    )
    assert (
        outcome["product_margin_triggered_months"],
        outcome["product_margin_unresolved_months"],
        outcome["product_negative_equity_months"],
    ) == (1, 0, 0)
    assert outcome["first_failure"] == outcome["first_product_failure"] is None
    assert product_totals([outcome])["joint_feasibility_fraction"] == 1
