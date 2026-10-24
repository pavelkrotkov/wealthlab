"""Freeze dollar rules while preserving actual-year age and high-earner catch-up treatment.

Birth dates deliberately cross age bands while the dollar table stays fixed.
Advancing a calendar year must not restore pretax high-earner catch-up or
silently label an assumed limit as a published rule.
"""

import pytest

from tests.future_contribution_cases import hsa, retirement
from wealthlab.retirement.contribution_inputs import ContributionCase
from wealthlab.retirement.contributions import run
from wealthlab.retirement.hsa import run as run_hsa
from wealthlab.retirement.hsa_inputs import HSACase


@pytest.mark.parametrize("birth,roth_limit", [("1990-06-15", 11250), ("1986-06-15", 8000)])
def test_workplace_catchup_uses_actual_age_but_frozen_wage_threshold(birth, roth_limit):
    result = run(retirement(birth=birth))
    assert result["rule_base_year"] == 2026
    assert result["rule_mode"] == "freeze_2026_assumption"
    owner = result["owners"][0]
    assert owner["pretax_401k"] == 24500
    assert owner["roth_401k"] == roth_limit
    assert owner["traditional_ira"] == owner["federal_ira_deduction"] == 8600


@pytest.mark.parametrize("year,limit", [(2049, 4400), (2050, 5400)])
def test_hsa_catchup_uses_calendar_age_not_rule_base(year, limit):
    result = run_hsa(hsa(year=year))
    assert result["contribution_limits"]["person"] == limit
    assert result["personal_federal_deduction"] == limit
    assert result["cash"] == 20000 - limit
    assert result["rule_base_year"] == 2026


@pytest.mark.parametrize("case,model", [(retirement, ContributionCase), (hsa, HSACase)])
def test_future_year_needs_explicit_rule_assumption(case, model):
    payload = case().model_dump(mode="json")
    payload.pop("rule_mode")
    with pytest.raises(ValueError, match="explicit future assumption"):
        model.model_validate(payload)


@pytest.mark.parametrize("case,model", [(retirement, ContributionCase), (hsa, HSACase)])
def test_freezing_does_not_backport_2026_limits(case, model):
    payload = case().model_dump(mode="json")
    payload["year"] = 2025
    with pytest.raises(ValueError, match="cannot apply before 2026"):
        model.model_validate(payload)
