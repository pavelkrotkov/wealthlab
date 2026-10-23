"""Debt principal, fees, transfers and shortfalls have different wealth effects."""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_debt_and_contribution_preserve_principal(payload):
    payload.update(end="2026-02-01", inflation=0)
    payload["accounts"][0]["monthly_fee"] = 10
    payload["debts"] = [
        dict(
            id="loan",
            provenance="assumption",
            currency="USD",
            balance=1200,
            annual_rate=0.12,
            monthly_payment=112,
        )
    ]
    transfer = dict(
        payload["expenses"][0], id="saving", destination="retirement", monthly_amount=1000
    )
    transfer.pop("category")
    payload["contributions"] = [transfer]
    row = project(Scenario.model_validate(payload))[0]
    assert row["interest"] == 12
    assert row["principal"] == 100
    assert row["closing_cash"] == 104_878
    assert row["account_balances"]["retirement"] == 101_000
    assert row["debt_balances"]["loan"] == 1100
    assert row["net_wealth"] == 204_778
