"""Receipt-date assets cannot finance an earlier order; annual basis is reconciled later."""

from decimal import Decimal

from wealthlab.retirement.distribution_inputs import DistributionCase
from wealthlab.retirement.distributions import run
from wealthlab.retirement.ira_rollover_example import synthetic


def test_a_later_rollover_does_not_fund_an_earlier_unfilled_withdrawal():
    data = synthetic().model_dump(mode="json")
    data["incoming_rollovers"][0]["date"] = "2026-07-01"
    result = run(DistributionCase.model_validate(data))
    row = result["orders"][0]
    assert row["paid"] == 10000
    assert row["unfilled"] == 5000
    assert result["cash"] == 10000
    assert result["account_balances"]["ira"] == 20000
    assert row["federal_basis_recovered"] == Decimal("1666.67")
    assert row["nj_basis_recovered"] == Decimal("2666.67")


def test_same_day_rollover_precedes_returns_and_withdrawals():
    data = synthetic().model_dump(mode="json")
    data["incoming_rollovers"][0]["date"] = "2026-06-01"
    data["returns"] = [
        dict(id="gain", provenance="illustration", date="2026-06-01", account_id="ira", rate=".10")
    ]
    result = run(DistributionCase.model_validate(data))
    assert result["market_change"] == 3000
    assert result["account_balances"]["ira"] == 18000
    assert result["cash"] == 15000
    assert result["orders"][0]["federal_basis_recovered"] == Decimal("2272.73")
