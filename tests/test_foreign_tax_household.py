"""Actual foreign payments conserve cash, claims and separate US liability.

Previously paid payroll is part of opening cash. Paying the foreign assessment
uses cash once, while its independently capped credit reduces only US income
tax. An unfunded native balance remains debt instead of negative wallet cash.
"""

from decimal import Decimal

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.tax.foreign_tax_example import synthetic


def test_actual_foreign_payment_and_native_credit_reconcile_ending_wealth_once():
    rows = project(synthetic())
    first = rows[0]
    assert first["foreign_tax_paid"] == Decimal(11000)
    assert first["foreign_tax_position"] == 0
    assert first["annual_tax"]["federal"]["foreign_tax_credit"] == Decimal("6724.50")
    assert not first["foreign_tax_unresolved"]
    assert total(rows, "foreign_tax_paid") == Decimal(11000)


def test_foreign_payment_and_domestic_settlement_reduce_opening_wealth_without_repaying_payroll():
    rows = project(synthetic())
    last = rows[-1]
    domestic = total(rows, "tax_settlement_paid")
    assert last["closing_cash"] == Decimal(50000) - Decimal(11000) - domestic
    assert last["net_wealth"] == last["closing_cash"]
    assert last["annual_tax"]["federal"]["employee_payroll"] == Decimal(7650)
    assert total(rows, "tax_withheld") == 0
    assert {r["funding_failure"] for r in rows} == {False}


def test_partial_native_settlement_retains_exact_cash_and_unpaid_claim():
    data = synthetic().model_dump(mode="json")
    data["accounts"][0]["balance"] = "7000"
    row = project(Scenario.model_validate(data))[0]
    assert row["foreign_tax_paid"] == Decimal("6999.99")
    assert row["closing_cash"] == Decimal(".01")
    assert row["foreign_tax_unfunded"] == Decimal("4000.01")
    assert row["foreign_tax_position"] == Decimal("4000.01")
    assert row["foreign_tax_positions"][0]["actual_net_paid_native"] == Decimal("6363.63")
    assert row["funding_failure"]
    assert row["net_wealth"] == Decimal(7000) - row["foreign_tax_paid"] - (
        row["foreign_tax_position"] + row["tax_position"]
    )


def total(rows, field):
    return sum((row[field] for row in rows), Decimal(0))
