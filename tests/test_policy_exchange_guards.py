"""Inactive paths cannot select their own basis, sponsor eligibility, fees or information.

Complete independently supplied profiles stay conditional; numerical tax facts
cannot become implicit K-1 scaling or permission to use a future source quote.
"""

import pytest
from optimization_cases import changed
from optimization_exchange_cases import case

from wealthlab.optimization.validation import validate


@pytest.mark.parametrize(
    "field,value,match",
    [
        ("source", "", "at least 1"),
        ("provenance", "unresolved", "resolved source"),
        ("available_on", "2026-02-01", "opening decision"),
        ("complete_cash_tax_and_basis_profile_confirmed", False, "projected envelope"),
        (
            "profile_valid_for_projected_income_and_market_paths_confirmed",
            False,
            "projected envelope",
        ),
    ],
)
def test_every_inactive_profile_requires_complete_available_source_facts(field, value, match):
    def edit(data):
        data["dimensions"][-1]["locked_choice"] = "retain"
        data["exchange_opportunities"][2][field] = value

    with pytest.raises(ValueError, match=match):
        validate(changed(case(), edit))


@pytest.mark.parametrize(
    "field,value",
    [
        ("annual_fee", "0.5"),
        ("federal_contribution", "denied"),
        ("accepted", False),
        ("liquid_after", "2026-01-01"),
    ],
)
def test_an_inactive_offer_cannot_change_fees_legal_treatment_or_contractual_availability(
    field, value
):
    profile = changed(
        case(), lambda d: d["exchange_opportunities"][1]["plan"].update({field: value})
    )
    with pytest.raises(ValueError, match="source stock, basis, eligibility"):
        validate(profile)


def test_partial_contribution_cannot_rewrite_the_original_whole_lot_basis():
    profile = changed(
        case(),
        lambda d: d["exchange_opportunities"][1]["plan"]["source_lot"].update(federal_basis="2000"),
    )
    with pytest.raises(ValueError, match="source stock, basis, eligibility"):
        validate(profile)


def test_observation_prices_locks_and_recognition_eligibility_remain_shared():
    def edit(data):
        data["exchange_opportunities"][1]["plan"]["observations"][0]["locked"] = True

    with pytest.raises(ValueError, match="prices and locks"):
        validate(changed(case(), edit))


def test_zero_contribution_requires_its_own_zero_fund_cash_and_tax_facts():
    profile = changed(
        case(),
        lambda d: d["exchange_opportunities"][0]["plan"]["observations"][0].update(
            distribution="100"
        ),
    )
    with pytest.raises(ValueError, match="Zero contribution"):
        validate(profile)


def test_missing_original_source_or_factor_map_cannot_create_a_new_book():
    profile = changed(case(), lambda d: d["household"].update(exchange_fund_plan=None))
    with pytest.raises(ValueError, match="original source book"):
        validate(profile)
    profile = changed(case(), lambda d: d["binding"].update(exchange_factors={}))
    with pytest.raises(ValueError, match="factor bindings"):
        validate(profile)


def test_an_undeclared_path_or_duplicate_offer_identifier_is_rejected():
    profile = changed(case(), lambda d: d["exchange_opportunities"][1].update(id="retain"))
    with pytest.raises(ValueError, match="identifiers must be unique"):
        validate(profile)
    profile = changed(
        case(), lambda d: d["dimensions"][-1]["choices"][1].update(exchange_path="unknown")
    )
    with pytest.raises(ValueError, match="supplied path"):
        validate(profile)


def test_source_loss_treatment_cannot_be_changed_as_an_allocation_decision():
    def edit(data):
        data["exchange_opportunities"][1]["plan"]["observations"][0]["allocation"]["federal_loss"][
            "eligibility_after_limits_assumed"
        ] = True

    with pytest.raises(ValueError, match="eligibility and recognition"):
        validate(changed(case(), edit))
