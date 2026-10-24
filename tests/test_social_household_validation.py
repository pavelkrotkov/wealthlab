"""Missing context and duplicated benefit sources must fail before a household result exists."""

import pytest

from wealthlab.retirement.social_household import prepare, template
from wealthlab.retirement.social_household_example import synthetic
from wealthlab.retirement.social_inputs import SocialCase
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import IncomeRule, TaxEvent


def test_requires_tax_plan_and_resolved_claim_inputs():
    case = synthetic()
    with pytest.raises(ValueError, match="annual tax plan"):
        prepare(case.model_copy(update=dict(tax_plan=None)))
    with pytest.raises(ValueError, match="Resolve critical Social Security"):
        SocialCase.model_validate(template(case))


def test_manual_benefit_income_cannot_duplicate_generated_claims():
    case = synthetic()
    rule = IncomeRule(income_id="interest", federal="social_security", new_jersey="none")
    plan = case.tax_plan.model_copy(update=dict(income_rules=[rule]))
    with pytest.raises(ValueError, match="manual Social Security income rules"):
        prepare(case.model_copy(update=dict(tax_plan=plan)))
    event = TaxEvent(
        date=case.start,
        description="Duplicate benefits",
        cash_received=100,
        federal=FederalIncome(social_security=100),
        new_jersey=NJIncome(),
    )
    plan = case.tax_plan.model_copy(update=dict(events=[event]))
    with pytest.raises(ValueError, match="manual Social Security events"):
        prepare(case.model_copy(update=dict(tax_plan=plan)))


def test_january_opening_facts_cannot_repeat_generated_benefits():
    case = synthetic()
    annual = case.tax_plan.cases[0]
    annual = annual.model_copy(update=dict(federal_income=FederalIncome(social_security=100)))
    plan = case.tax_plan.model_copy(update=dict(cases=[annual, *case.tax_plan.cases[1:]]))
    with pytest.raises(ValueError, match="January opening"):
        prepare(case.model_copy(update=dict(tax_plan=plan)))
