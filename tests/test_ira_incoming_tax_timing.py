"""Source rollover eligibility does not change IRA age tests or prior-year RMD values."""

from decimal import Decimal

from wealthlab.retirement.distribution_inputs import DistributionCase
from wealthlab.retirement.distributions import run
from wealthlab.retirement.ira_rollover_example import synthetic


def aged(data, birth, age):
    data["owners"][0]["birth_date"] = birth
    data["annual_tax_case"]["filing"]["age_primary"] = age
    if data["annual_tax_case"]["nj_filing"] is not None:
        data["annual_tax_case"]["nj_filing"]["age_primary"] = age
    return DistributionCase.model_validate(data)


def test_source_plan_eligibility_does_not_grant_an_ira_age55_exception():
    data = synthetic().model_dump(mode="json")
    result = run(aged(data, "1971-06-15", 55))
    assert result["orders"][0]["additional_tax"] == 1250
    assert not result["orders"][0]["early_penalty_exception"]


def test_incoming_value_does_not_inflate_the_prior_december_ira_rmd_base():
    data = synthetic().model_dump(mode="json")
    result = run(aged(data, "1951-06-15", 75))
    assert result["rmd"]["person"]["required"] == Decimal("406.51")
    assert result["rmd"]["person"]["shortfall"] == 0
