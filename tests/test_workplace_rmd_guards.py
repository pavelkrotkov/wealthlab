"""Incomplete plan identity, conflicting owners and unconfirmed relief cannot grant benefits."""

import pytest
from pydantic import ValidationError

from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace_rmd_example import synthetic
from wealthlab.retirement.workplace_rmd_validation import validate


@pytest.mark.parametrize(
    "sources",
    [
        ["alpha_one"],
        ["alpha_one", "alpha_one", "alpha_two"],
        ["alpha_one", "alpha_two", "beta"],
        ["alpha_one", "alpha_two", "unknown"],
    ],
)
def test_sources_cover_every_complete_pretax_account_once(sources):
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["cash_withdrawals"]["rmd"]["groups"]["alpha"]["sources"] = sources
    with pytest.raises(ValueError, match="cover each"):
        validate(Scenario.model_validate(data))


@pytest.mark.parametrize(
    "field",
    [
        "complete_distinct_plan_balances_and_distributions_confirmed",
        "beneficiary_table_eligibility_confirmed",
    ],
)
def test_unknown_plan_or_beneficiary_context_blocks_calculation(field):
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["cash_withdrawals"]["rmd"]["groups"]["alpha"][field] = False
    with pytest.raises(ValueError, match="Confirm"):
        validate(Scenario.model_validate(data))


def test_different_spouses_cannot_share_a_plan_requirement():
    data = synthetic().model_dump(mode="json")
    data["accounts"][2]["owner"] = "person_b"
    with pytest.raises(ValueError, match="one owner"):
        validate(Scenario.model_validate(data))


@pytest.mark.parametrize(
    "treatment", ["timely_correction_10_percent_assumption", "irs_waiver_allowed_assumption"]
)
def test_excise_relief_requires_explicit_contingent_assumptions(treatment):
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["cash_withdrawals"]["rmd"]["shortfall_treatment"] = treatment
    with pytest.raises(ValidationError, match="conditional"):
        Scenario.model_validate(data)


def test_manual_nj_rate_also_respects_noneligible_federal_withholding():
    data = synthetic().model_dump(mode="json")
    plan = data["workplace_plan"]["cash_withdrawals"]
    plan["rmd"]["noneligible_federal_withholding_rate"] = ".95"
    plan["orders"][0]["nj_withholding_rate"] = ".10"
    with pytest.raises(ValueError, match="withholding cannot"):
        validate(Scenario.model_validate(data))


def test_unmodeled_opening_failures_cannot_be_assumed_away():
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["cash_withdrawals"]["rmd"][
        "no_unmodeled_opening_shortfalls_confirmed"
    ] = False
    with pytest.raises(ValueError, match="opening"):
        validate(Scenario.model_validate(data))


def test_one_plan_cannot_use_conflicting_separation_histories_across_subaccounts():
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["cash_withdrawals"]["profiles"]["alpha_two"]["separation_date"] = (
        "2026-02-01"
    )
    with pytest.raises(ValueError, match="separation history"):
        validate(Scenario.model_validate(data))
