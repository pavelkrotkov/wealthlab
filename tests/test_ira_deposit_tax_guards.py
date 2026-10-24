"""Changed income must not silently preserve an unsupported IRA tax benefit."""

import pytest

from wealthlab.retirement.distribution_inputs import DistributionCase
from wealthlab.retirement.distributions import run
from wealthlab.retirement.ira_contribution_example import synthetic


def test_market_gain_that_removes_roth_eligibility_blocks_funded_deposit():
    data = synthetic().model_dump(mode="json")
    data["annual_tax_case"]["federal_income"]["long_term"] = "300000"
    with pytest.raises(ValueError, match="Funded Roth IRA contributions exceed"):
        run(DistributionCase.model_validate(data))


def test_completed_income_that_changes_deduction_requires_updated_forecast():
    data = synthetic().model_dump(mode="json")
    data["contributions"]["contributors"][0]["covered_by_workplace_plan"] = True
    data["annual_tax_case"]["federal_income"]["wages_primary"] = "250000"
    # Forecast no longer supports the maximum deduction initially taken.
    data["contributions"]["contributors"][0]["traditional_ira_magi"] = "50000"
    with pytest.raises(ValueError, match="changes the maximum deduction"):
        run(DistributionCase.model_validate(data))


def test_non_wage_compensation_requires_supported_adapter_in_annual_check():
    data = synthetic().model_dump(mode="json")
    data["annual_tax_case"]["federal_income"]["wages_primary"] = "0"
    with pytest.raises(ValueError, match="exceeds supported W-2 compensation"):
        run(DistributionCase.model_validate(data))


def test_missing_tax_case_keeps_eligibility_explicitly_conditional():
    data = synthetic().model_dump(mode="json")
    data["annual_tax_case"] = None
    result = run(DistributionCase.model_validate(data))
    assert result["contribution_eligibility"] == dict(status="supplied_annual_forecasts_only")
    assert result["annual_tax"] is None
