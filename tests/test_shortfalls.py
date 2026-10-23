"""Unfunded obligations are explicit, with no implicit borrowing or asset sales."""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_shortfall_never_creates_cash_or_sells_retirement(payload):
    payload.update(end="2026-03-01", incomes=[])
    payload["accounts"][0].update(balance=100, monthly_fee=10)
    rows = project(Scenario.model_validate(payload))
    assert rows[0]["essential"] == 90
    assert rows[0]["funding_shortfall"] == 3910
    assert rows[1]["closing_cash"] == 0
    assert rows[1]["fees_owed"] == 10
    assert rows[1]["net_wealth"] == 99_990


def test_currency_conversion_and_unpaid_interest(payload):
    payload.update(end="2026-02-01", incomes=[])
    payload["accounts"][0].update(balance=0)
    payload["debts"] = [
        dict(
            id="loan",
            provenance="assumption",
            currency="EUR",
            balance=1000,
            annual_rate=0.12,
            monthly_payment=100,
        )
    ]
    row = project(Scenario.model_validate(payload))[0]
    assert row["interest"] == 11
    assert row["debt_balances"]["loan"] == 1111
    assert row["principal"] == 0
    assert row["debt_shortfall"] == 110


def test_fee_arrears_are_paid_when_income_resumes(payload):
    payload.update(end="2026-03-01", expenses=[])
    payload["accounts"][0].update(balance=0, monthly_fee=10)
    payload["incomes"][0].update(start="2026-02-01", monthly_amount=100)
    rows = project(Scenario.model_validate(payload))
    assert rows[0]["fees_owed"] == 10
    assert rows[1]["fees"] == 20
    assert rows[1]["fees_owed"] == 0
    assert rows[1]["closing_cash"] == 80
