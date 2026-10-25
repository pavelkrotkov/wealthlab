"""Incomplete earned-month classification cannot bypass work-test or old no-work guards."""

import pytest
from social_work_household_cases import payload

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


@pytest.mark.parametrize(
    "change,match",
    [
        ("actual", "actual work wages unset"),
        ("partial", "complete calendar-year"),
        ("opening", "Manual/opening W2"),
        ("currency", "earned W2 streams require USD"),
        ("missing_claims", "requires generated Social Security"),
        ("no_work_policy", "Pre-FRA benefits"),
        ("missing_report", "complete work report"),
    ],
)
def test_household_work_profile_rejects_unsupported_inputs(change, match):
    data = payload()
    edits = {
        "actual": lambda: data["social_work_plan"]["years"][0].update(
            actual_monthly_wages=[0] * 12
        ),
        "partial": lambda: data.update(start="2026-02-01"),
        "opening": lambda: data["tax_plan"]["cases"][0]["federal_income"].update(wages_primary=1),
        "currency": lambda: data["incomes"][0].update(currency="EUR"),
        "missing_claims": lambda: data.update(social_security=None),
        "no_work_policy": lambda: data.update(social_work_plan=None),
        "missing_report": lambda: data["social_work_plan"]["years"].pop(),
    }
    edits[change]()
    data["usd_per_currency"]["EUR"] = 1
    with pytest.raises(ValueError, match=match):
        project(Scenario.model_validate(data))
