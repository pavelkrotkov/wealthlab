"""Actual NJ liabilities share the existing cash ledger with the foreign book.

Opening cash 50,000 minus foreign tax 11,000, US income tax 6,724.50 and two
NJ returns totaling 1,741.60 leaves 30,533.90. Previously paid payroll is not
paid again. A cash shortfall preserves the actual return balances as debt.
"""

from decimal import Decimal

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.tax.nj_residence_example import household_example


def test_nj_move_and_actual_foreign_cash_preserve_independent_us_tax_payroll_and_wealth():
    rows = project(household_example())
    final = rows[-1]
    assert sum(r["foreign_tax_paid"] for r in rows) == 11000
    assert (
        final["annual_tax"]["federal"]["foreign_tax_credit"],
        final["annual_tax"]["federal"]["employee_payroll"],
    ) == (Decimal("6724.50"), 7650)
    assert final["annual_tax"]["new_jersey"]["income_tax"] == Decimal("1741.60")
    assert final["closing_cash"] == Decimal("30533.90")
    assert final["net_wealth"] == final["closing_cash"]


def test_actual_settlement_is_allocated_to_both_return_identities_without_payable_netting():
    rows = project(household_example())
    state = rows[-1]["annual_tax"]["new_jersey"]["residence_returns"]
    assert [r["actual_payments"] for r in state] == [1244, Decimal("497.60")]
    assert {r["payable"] for r in state} == {0}
    assert not any(r["funding_failure"] for r in rows)


def test_insufficient_year_end_cash_allocates_only_actual_paid_state_and_retains_unpaid_tax():
    data = household_example().model_dump(mode="json")
    data["accounts"][0]["balance"] = "11500"
    final = project(Scenario.model_validate(data))[-1]
    returns = final["annual_tax"]["new_jersey"]["residence_returns"]
    assert [r["actual_payments"] for r in returns] == [500, 0]
    assert sum(r["payable"] for r in returns) == Decimal("1241.60")
    assert final["closing_cash"] == 0
    assert final["tax_owed"] == final["tax_position"]
    assert final["net_wealth"] == -final["tax_position"]
    assert final["funding_failure"]


@pytest.mark.parametrize(
    "change, message",
    [
        (lambda d: d["tax_plan"].update(nj_wage_withholding=".01"), "prepayments"),
        (lambda d: d["tax_plan"].update(settlement_timing="monthly_accrued"), "year-end"),
        (lambda d: d["tax_plan"]["cases"][0]["payments"].update(nj_withheld="100"), "Opening NJ"),
        (
            lambda d: d["tax_plan"]["cases"][0]["nj_residence"]["people"][0].update(id="other"),
            "stable filing",
        ),
    ],
)
def test_unsafe_unallocated_payments_and_owner_swaps_do_not_produce_favorable_cash(change, message):
    data = household_example().model_dump(mode="json")
    change(data)
    with pytest.raises(ValueError, match=message):
        project(Scenario.model_validate(data))


def test_dated_wages_cross_the_actual_move_month_without_early_income_or_cash_recognition():
    data = household_example().model_dump(mode="json")
    data.update(start="2025-01-01", foreign_tax_plan=None)
    data["accounts"][0]["balance"] = "0"
    case = data["tax_plan"]["cases"][0]
    case["federal_income"]["wages_primary"] = "0"
    case["nj_income"]["wages"] = "0"
    case["payments"]["employee_payroll_withheld"] = "0"
    profile = case["nj_residence"]
    for source, amount in zip(profile["income"], [30000, 15000, 15000], strict=True):
        source["amount"] = str(amount)
    data["tax_plan"]["events"] = [
        dict(
            date=when,
            description="Synthetic actual wage receipt",
            cash_received="30000",
            federal=dict(wages_primary="30000"),
            new_jersey=dict(wages="30000"),
        )
        for when in ["2025-06-30", "2025-09-30"]
    ]
    rows = project(Scenario.model_validate(data))
    assert rows[4]["closing_cash"] == rows[4]["annual_tax"]["new_jersey"]["income_tax"] == 0
    assert [rows[i]["annual_tax"]["new_jersey"]["income_tax"] for i in [5, 7, 8]] == [
        447,
        447,
        Decimal("670.50"),
    ]
    assert rows[-1]["annual_tax"]["federal"]["employee_payroll"] == 4590
    assert rows[-1]["closing_cash"] == Decimal("49668.00")
