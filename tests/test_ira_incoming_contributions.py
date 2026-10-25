"""An eligible rollover has its own basis and neither spends annual room nor funds deposits."""

import pytest
from incoming_rollover_cases import combined

from wealthlab.retirement.distribution_inputs import DistributionCase
from wealthlab.retirement.distributions import run


def test_received_plan_assets_cannot_fund_ordinary_contributions():
    result = run(DistributionCase.model_validate(combined(0)))
    assert [r["eligible"] for r in result["contribution_orders"]] == [3000, 3000]
    assert [r["funded"] for r in result["contribution_orders"]] == [0, 0]
    assert result["account_balances"]["ira"] == 30000
    assert result["cash"] == 0


def test_outside_cash_funds_deposits_without_using_rollover_value_as_annual_room():
    result = run(DistributionCase.model_validate(combined(10000)))
    person = result["contribution_owners"][0]
    assert [r["funded"] for r in result["contribution_orders"]] == [3000, 3000]
    assert person["federal_ira_deduction"] == 3000
    assert result["owners"][0]["federal_ira_basis"] == 5000
    assert result["owners"][0]["nj_ira_basis"] == 11000
    assert result["cash"] == 4000
    assert sum(result["account_balances"].values()) + result["cash"] == 40000


def test_a_rollover_id_cannot_collide_with_an_ordinary_contribution():
    data = combined(10000)
    data["incoming_rollovers"][0]["id"] = data["contributions"]["orders"][0]["id"]
    with pytest.raises(ValueError, match="unique IDs"):
        DistributionCase.model_validate(data)
