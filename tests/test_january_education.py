"""A finalized NJ return changes the actual funded NJBEST deduction audit."""

from tests.january_consumer_cases import data
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.education_household_example import plan


def test_january_loss_rechecks_the_njbest_income_threshold():
    case = data(150000)
    case["accounts"].append(
        dict(
            id="college",
            provenance="illustration",
            owner="person_a",
            wrapper="education",
            currency="USD",
            balance="30000",
            monthly_fee="0",
        )
    )
    case["education_plan"] = plan()
    rows = project(Scenario.model_validate(case))
    revision = rows[-1]["lot_audit"]["return_reconciliations"][0]
    education = rows[-1]["education_audit"]["years"][0]
    assert revision["old_result"]["new_jersey"]["gross_income"] == 210000
    assert revision["final_result"]["new_jersey"]["gross_income"] == 194000
    assert education["njbest_potential_deduction"] == 6000
    assert education["income_finalized"] == "january_wash_reconciliation"
    assert revision["final_result"]["new_jersey"]["taxable_income"] == 186000
