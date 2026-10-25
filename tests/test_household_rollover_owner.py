"""A source may not transfer tax ownership or masquerade as a designated Roth rollover."""

import pytest
from plan_rollover_rmd_cases import rmd_data, transfer

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_another_spouses_ira_is_not_an_eligible_direct_destination():
    data = rmd_data()
    data["accounts"][-1]["owner"] = "person_b"
    data["workplace_plan"]["cash_withdrawals"]["direct_rollovers"] = [
        transfer("foreign_owner", "alpha_one", "2026-02-01"),
    ]
    with pytest.raises(ValueError, match="preserve the source account owner"):
        project(Scenario.model_validate(data))


def test_a_roth_ira_needs_its_own_direct_conversion_profile():
    data = rmd_data()
    data["accounts"][-1]["wrapper"] = "roth"
    data["ira_plan"]["products"]["ira"] = "roth_ira"
    data["workplace_plan"]["cash_withdrawals"]["direct_rollovers"] = [
        transfer("roth_direct", "alpha_one", "2026-02-01"),
    ]
    with pytest.raises(ValueError, match="ordinary traditional IRA target"):
        project(Scenario.model_validate(data))
