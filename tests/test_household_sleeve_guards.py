"""No invented reserve, overlapping funding book or incomplete return schedule is executable."""

import pytest
from household_sleeve_cases import flat

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


@pytest.mark.parametrize(
    "mutation", ["reserve", "opening", "observation", "confirmation", "provenance", "funding"]
)
def test_invalid_household_sleeve_scope_blocks(mutation):
    data = flat().model_dump(mode="json")
    sleeve = data["sleeve_plan"]["sleeves"][0]
    if mutation == "reserve":
        sleeve["case"]["outside_cash"] = "10000"
    elif mutation == "opening":
        sleeve["case"]["opening_equity"] = "200000"
    elif mutation == "observation":
        sleeve["observations"].pop()
    elif mutation == "confirmation":
        sleeve["all_tax_recognition_and_exit_assumptions_supplied_confirmed"] = False
    elif mutation == "provenance":
        sleeve["observations"][0]["provenance"] = "unresolved"
    else:
        data["tax_plan"]["funding_sources"] = [
            dict(
                account_id="sleeve",
                federal_basis=100000,
                nj_basis=100000,
                federal_character="long_term",
                loss_treatment="allowed",
                liquid_after="2026-01-01",
            )
        ]
    with pytest.raises(ValueError):
        project(Scenario.model_validate(data))


def test_supplied_tax_allocation_cannot_introduce_a_personal_hsa_deduction():
    data = flat().model_dump(mode="json")
    data["sleeve_plan"]["sleeves"][0]["allocations"] = [
        dict(
            id="bad_tax",
            provenance="assumption",
            date="2026-01-31",
            federal=dict(deductible_hsa_contributions=1000),
            new_jersey={},
        )
    ]
    with pytest.raises(ValueError, match="Unsupported federal character"):
        project(Scenario.model_validate(data))
