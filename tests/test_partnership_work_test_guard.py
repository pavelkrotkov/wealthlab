"""Partnership earnings cannot silently bypass the earned-W2-only SSA work adapter."""

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.social_work_household_example import synthetic


@pytest.mark.parametrize("amount", ["1000", "-1000"])
@pytest.mark.parametrize("origin", ["annual", "event"])
def test_ssa_work_household_rejects_unclassified_partnership_earnings(amount, origin):
    data = synthetic().model_dump(mode="json")
    income = dict(partnership_se_earnings_primary=amount)
    if origin == "annual":
        data["tax_plan"]["cases"][0]["federal_income"].update(income)
    else:
        data["tax_plan"]["events"].append(
            dict(
                date="2026-01-31",
                description="Synthetic supplied partnership earnings",
                cash_received="0",
                federal=income,
                new_jersey={},
            )
        )
    with pytest.raises(ValueError, match="Partnership SE needs earned-month classification"):
        project(Scenario.model_validate(data))
