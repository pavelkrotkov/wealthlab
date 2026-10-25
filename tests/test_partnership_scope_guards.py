"""New earned inputs cannot silently bypass older no-work and W-2-only retirement profiles."""

from datetime import date

import pytest
from ordinary_income_cases import compute

from tests.test_social_household_work import early_case
from wealthlab.retirement.distribution_inputs import DistributionCase
from wealthlab.retirement.distributions import run
from wealthlab.retirement.ira_contribution_example import synthetic
from wealthlab.retirement.social_household import prepare
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import TaxEvent


def test_supplied_partnership_se_earnings_invalidate_the_old_pre_fra_no_work_bridge():
    case = early_case()
    event = TaxEvent(
        date=date(2030, 1, 1),
        description="Supplied box14 earnings",
        cash_received=0,
        federal=FederalIncome(partnership_se_earnings_primary=100),
        new_jersey=NJIncome(),
    )
    plan = case.tax_plan.model_copy(update={"events": [event]})
    with pytest.raises(ValueError, match="Pre-FRA benefits with annual wages"):
        prepare(case.model_copy(update={"tax_plan": plan}))


def test_combined_ira_compensation_cannot_ignore_partnership_se_earnings():
    data = synthetic().model_dump(mode="json")
    data["annual_tax_case"]["federal_income"]["partnership_se_earnings_primary"] = "100"
    with pytest.raises(ValueError, match="Partnership SE compensation"):
        run(DistributionCase.model_validate(data))


def test_single_return_rejects_spouse_partnership_se_earnings():
    with pytest.raises(ValueError, match="Spouse wage"):
        compute(dict(partnership_se_earnings_spouse=100))
