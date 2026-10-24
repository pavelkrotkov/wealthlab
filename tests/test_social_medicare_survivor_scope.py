"""A real pure-survivor claim reaches the household mortality guard before collection."""

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.social import run
from wealthlab.retirement.social_medicare_example import synthetic


def test_pure_survivor_requires_household_mortality_instead_of_smi_record_selection():
    data = synthetic().model_dump(mode="json")
    claims = data["social_security"]
    claims["survival_policy"] = "dated_deaths"
    claims["members"][0].update(death_date="2031-07-15", spousal_eligibility_confirmed=False)
    claims["members"][1].update(
        own_insured=False,
        pia_january_2026="0",
        survivor_claim_month="2031-07-01",
        survivor_eligibility_confirmed=True,
    )
    scenario = Scenario.model_validate(data)
    assert any(r["survivor_excess"] > 0 for r in run(scenario.social_security)["cash_months"])
    with pytest.raises(ValueError, match="Dated deaths require the standalone claim workbench"):
        project(scenario)
