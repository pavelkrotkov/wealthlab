"""Payment-in-horizon and earnings-test year are different calendar decisions.

The June entitlement paid in July still depends on that year's pre-FRA work.
A prior December paid in January does not become subject to new post-FRA wages.
"""

from datetime import date

import pytest

from wealthlab.household.scenario import Scenario
from wealthlab.retirement.social_household import prepare
from wealthlab.retirement.social_household_example import synthetic
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.projection_example import annual_case


def boundary_case(month):
    payload = synthetic().model_dump(mode="json")
    payload["start"] = date(2030, month, 1)
    born = date(1963, month, 2)
    payload["members"][0]["birth_date"] = born
    payload["social_security"]["members"][0].update(
        birth_date=born, claim_month=date(2025, month, 1)
    )
    case = Scenario.model_validate(payload)
    assert case.tax_plan is not None
    cases = [annual_case(case, year) for year in range(2030, 2033)]
    cases[0] = cases[0].model_copy(update=dict(federal_income=FederalIncome(wages_primary=100)))
    plan = case.tax_plan.model_copy(update=dict(cases=cases))
    return case.model_copy(update=dict(tax_plan=plan))


def test_pre_start_entitlement_paid_inside_the_year_checks_opening_earnings():
    with pytest.raises(ValueError, match="Pre-FRA benefits with annual wages"):
        prepare(boundary_case(7))


def test_prior_december_is_not_retested_against_post_fra_january_wages():
    prepared = prepare(boundary_case(1))
    january = [i for i in prepared.incomes[1:] if i.start == date(2030, 1, 1)]
    assert sum(i.monthly_amount for i in january) == 1750
