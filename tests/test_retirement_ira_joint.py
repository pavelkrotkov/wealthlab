"""Spousal compensation and IRA aggregation must not depend on account count."""

import pytest
from test_retirement_contributions import calculate, case_for


def test_multiple_destinations_share_the_same_ira_limit():
    data = case_for("traditional_ira", amount="6000.00", roth_ira_magi="100000.00")
    data["orders"].append(
        dict(data["orders"][0], id="roth_order", destination="rothira", kind="roth_ira")
    )
    result = calculate(data)
    assert [item["funded"] for item in result["orders"]] == [6000, 2600]


def test_joint_spousal_budget_can_fund_owner_without_earnings():
    data = case_for("traditional_ira", amount="8600.00", ira_compensation_budget="10000.00")
    spouse = dict(
        data["contributors"][0],
        id="spouse",
        eligible_ira_compensation="0.00",
        ira_compensation_budget="8600.00",
        covered_by_workplace_plan=False,
        traditional_ira_magi="200000.00",
    )
    data["contributors"].append(spouse)
    data["filing"] = "joint"
    data["accounts"].append(dict(data["accounts"][2], id="spouse_ira", owner="spouse"))
    data["orders"].append(
        dict(data["orders"][0], id="spouse_order", owner="spouse", destination="spouse_ira")
    )
    result = calculate(data)
    assert result["owners"][0]["federal_ira_deduction"] == 0
    assert result["owners"][1]["federal_ira_deduction"] == 8600
    data["contributors"][0]["ira_compensation_budget"] = "200000.00"
    with pytest.raises(ValueError, match="combined eligible compensation"):
        calculate(data)


@pytest.mark.parametrize(
    ("covered", "spouse", "lived", "expected"),
    [
        (False, False, True, 8600),
        (False, True, True, 0),
        (True, False, True, 0),
        (True, False, False, 8600),
    ],
)
def test_separate_filer_coverage_and_living_apart(covered, spouse, lived, expected):
    data = case_for(
        "traditional_ira", covered_by_workplace_plan=covered, traditional_ira_magi="20000.00"
    )
    data.update(filing="separate", spouse_covered_by_workplace_plan=spouse, lived_with_spouse=lived)
    assert calculate(data)["owners"][0]["federal_ira_deduction"] == expected


def test_no_compensation_does_not_create_minimum_roth_permission():
    data = case_for(
        "roth_ira",
        eligible_ira_compensation="0.00",
        ira_compensation_budget="0.00",
        roth_ira_magi="167999.00",
    )
    assert calculate(data)["orders"][0]["funded"] == 0
