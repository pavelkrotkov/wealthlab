"""Every offered contract and inactive retirement choice must have matching complete facts."""

from datetime import date

import pytest
from optimization_employment_cases import changed, flat

from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.inputs import PolicyChoice
from wealthlab.optimization.validation import validate


@pytest.mark.parametrize(
    "edit,message",
    [
        (
            lambda p: p["dimensions"][0]["choices"][0].update(employment_offer="later"),
            "match every",
        ),
        (lambda p: p["dimensions"][0]["choices"][0].update(employment_offer=None), "atomically"),
        (
            lambda p: p["dimensions"][0]["choices"][0].update(employment_offer="missing"),
            "supplied complete",
        ),
        (lambda p: p.update(employment_offers=[]), "Supply employer independence"),
        (lambda p: p["employment_offers"][0].update(source="          "), "Resolve the source"),
        (lambda p: p["employment_offers"][0].update(available_on="2026-01-02"), "opening decision"),
        (lambda p: p["employment_offers"][0].update(source_date="2026-01-02"), "opening decision"),
        (
            lambda p: p["employment_offers"][0].update(
                all_candidate_income_and_market_paths_confirmed=False
            ),
            "complete employer",
        ),
    ],
)
def test_locked_inactive_profile_or_choice_is_still_validated(edit, message):
    profile = changed(edit)
    data = profile.model_dump(mode="json")
    data["dimensions"][0]["locked_choice"] = "later"
    from wealthlab.optimization.inputs import PolicySearch

    with pytest.raises(ValueError, match=message):
        validate(PolicySearch.model_validate(data))


def test_compiler_checks_actual_combined_dates_even_for_ad_hoc_selection():
    case = flat()
    bad = PolicyChoice(
        id="bad", retirement_dates={"person_a": date(2026, 1, 1)}, employment_offer="later"
    )
    with pytest.raises(ValueError, match="Candidate retirement dates"):
        compile_candidate(case, [bad])


@pytest.mark.parametrize(
    "edit,message",
    [
        (
            lambda p: p["employment_offers"][0]["compensation_plan"]["tranches"][0].update(
                opening_vested="30000"
            ),
            "tranches, rights",
        ),
        (
            lambda p: p["employment_offers"][0]["compensation_plan"]["tranches"][0].update(
                liquid_from="2027-01-01"
            ),
            "tranches, rights",
        ),
        (
            lambda p: p["employment_offers"][0]["employment_plan"]["paths"][0].update(
                opening_multiplier="2"
            ),
            "opening pay",
        ),
        (
            lambda p: p["employment_offers"][0]["employment_plan"]["paths"][0].update(
                income_ids=["missing"]
            ),
            "wage streams",
        ),
        (lambda p: p["employment_offers"][0]["retirement_dates"].pop("person_b"), "every member"),
        (
            lambda p: p["employment_offers"][1]["compensation_plan"]["events"][0].update(
                amount="90000"
            ),
            "original household",
        ),
    ],
)
def test_profiles_cannot_rewrite_opening_assets_rights_or_original_baseline(edit, message):
    with pytest.raises(ValueError, match=message):
        validate(changed(edit))
