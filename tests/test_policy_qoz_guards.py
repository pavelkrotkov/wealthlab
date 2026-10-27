"""Complete inactive contracts and underlying tax assumptions cannot become favorable controls."""

import pytest
from optimization_qoz_cases import case, changed

from wealthlab.optimization.validation import validate


@pytest.mark.parametrize(
    "field,value",
    [
        ("federal", "denied"),
        ("new_jersey", "denied"),
        ("carry_fraction", ".1"),
        ("settlement_months", 2),
        ("sale_not_before", "2027-11-30"),
    ],
)
def test_locked_no_entry_cannot_hide_changed_underlying_tax_or_contract_facts(field, value):
    def edit(data):
        data["dimensions"][0]["locked_choice"] = "no_entry"
        data["qoz_offers"][2]["plan"][field] = value

    with pytest.raises(ValueError, match="Keep QOZ"):
        validate(changed(case(), edit))


@pytest.mark.parametrize(
    "field,value",
    [
        ("source", "          "),
        ("source_date", "2027-01-02"),
        ("complete_cash_tax_and_terms_confirmed", False),
        ("profile_valid_for_all_candidate_income_and_paths_confirmed", False),
        ("provenance", "unresolved"),
    ],
)
def test_inactive_source_and_validity_facts_are_required_before_any_policy_runs(field, value):
    with pytest.raises(ValueError):
        validate(changed(case(), lambda d: d["qoz_offers"][1].update({field: value})))


def test_declined_entry_requires_no_prior_interest_confirmation():
    with pytest.raises(ValueError, match="no prior QOZ"):
        validate(
            changed(
                case(),
                lambda d: d["qoz_offers"][0].update(
                    declined_no_prior_interest_or_obligations_confirmed=False
                ),
            )
        )


def test_active_offer_cannot_claim_it_also_declines_entry():
    with pytest.raises(ValueError, match="cannot also"):
        validate(
            changed(
                case(),
                lambda d: d["qoz_offers"][2].update(
                    declined_no_prior_interest_or_obligations_confirmed=True
                ),
            )
        )
