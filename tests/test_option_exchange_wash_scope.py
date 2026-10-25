"""Known cross-book identities cannot contradict either declared no-wash profile."""

import pytest

from tests.option_exchange_cases import combined
from wealthlab.household.scenario import Scenario
from wealthlab.products.exchange_fund_validation import validate as validate_exchange
from wealthlab.products.option_household_validation import validate as validate_options


@pytest.mark.parametrize("owner", ["options", "exchange"])
def test_each_owner_rejects_known_shared_wash_groups_across_distinct_accounts(owner):
    data = combined()
    data["exchange_fund_plan"]["source_security"]["wash_group"] = "STOCK"
    scenario = Scenario.model_validate(data)
    with pytest.raises(ValueError, match="known wash group"):
        if owner == "options":
            validate_options(scenario, None)
        else:
            validate_exchange(scenario)
