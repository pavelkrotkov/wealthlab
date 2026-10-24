"""Changing work income must invalidate a pre-FRA no-deduction assumption.

Annual earnings can precede a claim. Tests include opening facts and dated
recognition, since checking only cash earned after the claim misses that case.
"""

from datetime import date

import pytest

from wealthlab.household.scenario import Scenario
from wealthlab.retirement.social_household import prepare
from wealthlab.retirement.social_household_example import synthetic
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_example import annual_case
from wealthlab.tax.projection_inputs import IncomeRule, TaxEvent


def early_case():
    payload = synthetic().model_dump(mode="json")
    payload["members"][0]["birth_date"] = "1965-01-02"
    payload["members"][0]["retirement_date"] = "2030-07-01"
    payload["social_security"]["members"][0].update(
        birth_date="1965-01-02", claim_month="2030-07-01"
    )
    case = Scenario.model_validate(payload)
    assert case.tax_plan is not None
    plan = case.tax_plan.model_copy(
        update=dict(cases=[annual_case(case, year) for year in range(2030, 2033)])
    )
    return case.model_copy(update=dict(tax_plan=plan))


def test_pre_claim_wages_cannot_preserve_a_no_deduction_confirmation():
    case = early_case()
    wage = case.incomes[0].model_copy(update=dict(stop_at_retirement=True))
    rule = IncomeRule(income_id=wage.id, federal="wages_primary", new_jersey="wages")
    plan = case.tax_plan.model_copy(update=dict(income_rules=[rule]))
    with pytest.raises(ValueError, match="Pre-FRA benefits with annual wages"):
        prepare(case.model_copy(update=dict(incomes=[wage], tax_plan=plan)))


@pytest.mark.parametrize("source", ["opening", "event"])
def test_opening_and_dated_wages_also_recheck_the_work_assumption(source):
    case = early_case()
    income = FederalIncome(wages_primary=100)
    if source == "opening":
        first = case.tax_plan.cases[0].model_copy(update=dict(federal_income=income))
        plan = case.tax_plan.model_copy(update=dict(cases=[first, *case.tax_plan.cases[1:]]))
    else:
        event = TaxEvent(
            date=date(2030, 1, 1),
            description="Wages",
            cash_received=100,
            federal=income,
            new_jersey=NJIncome(wages=100),
        )
        plan = case.tax_plan.model_copy(update=dict(events=[event]))
    with pytest.raises(ValueError, match="Pre-FRA benefits with annual wages"):
        prepare(case.model_copy(update=dict(tax_plan=plan)))


def test_early_claim_without_wages_and_post_fra_wages_remain_supported():
    assert prepare(early_case()).social_security is None
    case = synthetic()
    rule = IncomeRule(income_id="interest", federal="wages_primary", new_jersey="wages")
    plan = case.tax_plan.model_copy(update=dict(income_rules=[rule]))
    assert prepare(case.model_copy(update=dict(tax_plan=plan))).social_security is None
