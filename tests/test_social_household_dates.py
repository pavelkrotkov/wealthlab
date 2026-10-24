"""Aligned claim/tax dates prevent prorated checks or an unsupported survivor household."""

from datetime import date

import pytest

from wealthlab.retirement.social_household import prepare
from wealthlab.retirement.social_household_example import synthetic


def test_partial_month_cannot_prorate_a_whole_social_security_check():
    case = synthetic().model_copy(update=dict(start=date(2030, 1, 2)))
    with pytest.raises(ValueError, match="whole calendar months"):
        prepare(case)


def test_claim_case_must_cover_the_household_horizon():
    case = synthetic()
    social = case.social_security.model_copy(update=dict(end_year=2032))
    with pytest.raises(ValueError, match="cover the household"):
        prepare(case.model_copy(update=dict(social_security=social)))


def test_birth_dates_must_match_the_household():
    case = synthetic()
    first = case.social_security.members[0].model_copy(update=dict(birth_date=date(1960, 1, 3)))
    social = case.social_security.model_copy(
        update=dict(members=[first, case.social_security.members[1]])
    )
    with pytest.raises(ValueError, match="birth dates must match"):
        prepare(case.model_copy(update=dict(social_security=social)))


def test_dated_death_needs_the_standalone_workbench_until_household_mortality_lands():
    case = synthetic()
    first = case.social_security.members[0].model_copy(update=dict(death_date=date(2031, 7, 15)))
    social = case.social_security.model_copy(
        update=dict(
            members=[first, case.social_security.members[1]], survival_policy="dated_deaths"
        )
    )
    with pytest.raises(ValueError, match="Dated deaths require"):
        prepare(case.model_copy(update=dict(social_security=social)))


@pytest.mark.parametrize("field", ["filing", "nj_filing"])
def test_tax_ages_must_match_the_claim_and_household_birth_dates(field):
    case = synthetic()
    annual = case.tax_plan.cases[0]
    filing = getattr(annual, field).model_copy(update=dict(age_primary=69))
    annual = annual.model_copy(update={field: filing})
    plan = case.tax_plan.model_copy(update=dict(cases=[annual, *case.tax_plan.cases[1:]]))
    with pytest.raises(ValueError, match="tax ages must match"):
        prepare(case.model_copy(update=dict(tax_plan=plan)))


def test_separate_return_benefit_tax_requires_explicit_treatment():
    case = synthetic()
    first = case.social_security.members[0].model_copy(
        update=dict(partner=None, spousal_eligibility_confirmed=False)
    )
    social = case.social_security.model_copy(update=dict(members=[first]))
    cases = [
        annual.model_copy(
            update=dict(
                filing=annual.filing.model_copy(update=dict(status="separate", age_spouse=0)),
                nj_filing=annual.nj_filing.model_copy(update=dict(status="separate", age_spouse=0)),
            )
        )
        for annual in case.tax_plan.cases
    ]
    plan = case.tax_plan.model_copy(update=dict(cases=cases))
    case = case.model_copy(
        update=dict(members=[case.members[0]], social_security=social, tax_plan=plan)
    )
    with pytest.raises(ValueError, match="Separate-return Social Security"):
        prepare(case)
