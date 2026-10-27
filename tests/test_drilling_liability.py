"""Supplied recourse can consume outside cash and leave losses beyond invested capital.

Capital-call obligations do not duplicate creditor liabilities in net wealth.
The synthetic unlimited-recourse claim must remain after the account reaches zero.
"""

from drilling_cases import change, short

from wealthlab.household.projection import project


def test_creditor_claim_exceeds_initial_capital_and_retains_unpaid_recourse_once():
    def configure(data):
        row = data["drilling_plan"]["observations"][0]
        row.update(liability_cost="300000", residual_property_value="0", exit_gross_proceeds="0")
        row["deductions"][0].update(
            federal_requested="310000",
            nj_requested="310000",
            federal_basis_reduction="310000",
            nj_basis_reduction="310000",
            at_risk_reduction="310000",
        )

    row = project(change(short(), configure))[0]
    assert (row["drilling_call_funded"], row["drilling_recourse_funded"]) == (100000, 100000)
    assert (row["drilling_creditor_payables"], row["drilling_recourse_liability"]) == (
        200000,
        200000,
    )
    assert row["account_balances"]["drilling"] == 0
    assert row["closing_cash"] == 0
    assert row["net_wealth"] == -200000
    assert row["drilling_blocked_exit"]
    assert row["drilling_product_failure"]


def test_unfunded_call_does_not_add_a_second_wealth_liability_to_the_same_creditors():
    def configure(data):
        data["accounts"][0]["balance"] = "0"
        data["drilling_plan"]["observations"][0].update(
            residual_property_value="0", exit_gross_proceeds="0"
        )

    row = project(change(short(), configure))[0]
    assert row["drilling_call_owed"] == 100000
    assert row["drilling_creditor_payables"] == 100000
    assert row["drilling_recourse_liability"] == 100000
    assert row["net_wealth"] == -100000
    assert row["drilling_federal_basis"] == 0
    assert all(d["limited_amount"] == 0 for d in row["drilling_deduction_audit"])
