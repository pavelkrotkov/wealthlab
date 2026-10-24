"""Independent annual-limit, basis and cash-conservation expectations."""

from wealthlab.retirement.contribution_example import synthetic
from wealthlab.retirement.contribution_inputs import ContributionCase
from wealthlab.retirement.contributions import run


def case_for(kind, amount="100000.00", **person):
    data = synthetic().model_dump(mode="json")
    data["opening_cash"] = "200000.00"
    data["contributors"][0].update(person)
    order = next(item for item in data["orders"] if item["kind"] == kind)
    order["amount"] = amount
    data["orders"] = [order]
    return data


def calculate(data):
    return run(ContributionCase.model_validate(data))


def test_high_earner_catchup_and_insufficient_cash_are_separate():
    result = run(synthetic())
    assert [row["funded"] for row in result["orders"]] == [24500, 11250, 4250, 0]
    assert result["orders"][0]["blocked_by_limit"] == 11250
    assert result["orders"][2]["unfunded"] == 4350
    owner = result["owners"][0]
    assert owner["federal_ira_deduction"] == 0
    assert owner["new_federal_ira_basis"] == owner["new_nj_ira_basis"] == 4250
    assert sum(result["account_balances"].values()) + result["cash"] == 40000
