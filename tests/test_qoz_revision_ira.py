"""Original IRA deductions/basis remain fixed while revised MAGI is actually rechecked."""

from qoz_transition_cases import transition

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.ira_deposit_household_example import synthetic


def test_prior_year_qoz_election_preserves_posted_nondeductible_ira_basis():
    data = synthetic().model_dump(mode="json")
    product = transition().model_dump(mode="json")
    data["accounts"].extend(product["accounts"][1:])
    data.update(lot_plan=product["lot_plan"], qoz_plan=product["qoz_plan"])
    for year in data["ira_plan"]["contributions"]["years"]:
        year["contributors"][0].update(
            covered_by_workplace_plan=True, traditional_ira_magi="200000"
        )
    rows = project(Scenario.model_validate(data))
    original = rows[11]["ira_annual_reconciliation"]["contribution_owners"][0]
    revised = rows[-1]["qoz_audit"]["source_return_revisions"][0]
    assert original["new_federal_ira_basis"] == 3000
    assert original["federal_ira_deduction"] == 0
    assert (
        revised["ira_eligibility"]["traditional_ira_magi"] < revised["old_result"]["federal"]["agi"]
    )
    assert revised["ira_eligibility"]["status"] == "checked_supported_annual_w2_case"
