"""The uninvested profile cannot receive fund-generated cash, tax allocations or basis benefits."""

import pytest
from exchange_allocation_cases import allocated

from wealthlab.household.scenario import Scenario
from wealthlab.products.exchange_fund_household import Ledger


@pytest.mark.parametrize(
    "kind",
    [
        "distribution",
        "federal_basis_adjustment",
        "nj_basis_adjustment",
        "federal_income",
        "nj_income",
    ],
)
def test_zero_contribution_rejects_independently_supplied_fund_only_facts(kind):
    data = allocated(0).model_dump(mode="json")
    observation = data["exchange_fund_plan"]["observations"][0]
    if kind == "federal_income":
        observation["allocation"]["federal"]["interest"] = "100"
    elif kind == "nj_income":
        observation["allocation"]["new_jersey"]["interest"] = "100"
    else:
        observation[kind] = "100"
    with pytest.raises(ValueError, match="Zero contribution"):
        Ledger(Scenario.model_validate(data))
