"""Even inactive offers retain original sources, fixed product assumptions and explicit bounds.

No amount of available cash can authorize rewriting an existing holding or
selecting a different tax-basis history. All offered contracts validate before
sampling, so locking the cash-only choice cannot conceal a malformed product.
"""

import pytest
from optimization_allocation_cases import case
from optimization_cases import changed

from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.validation import validate


@pytest.mark.parametrize(
    "edit,match",
    [
        (lambda o: o.update(opening_cash_purchase_assumed_confirmed=False), "Confirm opening cash"),
        (
            lambda o: o.update(proportional_dollar_schedules_assumed_confirmed=False),
            "Confirm opening cash",
        ),
        (lambda o: o.update(provenance="unresolved"), "Confirm opening cash"),
        (
            lambda o: o.update(replace_observations_with_shared_paths_confirmed=False),
            "Confirm opening cash",
        ),
        (lambda o: o.update(cash_account="brokerage"), "existing USD cash"),
        (lambda o: o.update(cash_account="unknown"), "existing USD cash"),
        (lambda o: o["unit"].update(account_id="brokerage"), "new distinct account"),
        (lambda o: o["unit"]["case"].update(long_factor="unknown"), "shared market factors"),
        (
            lambda o: o["unit"]["private_fund_contract"].update(federal_opening_basis="11000"),
            "bases equal to cost",
        ),
        (lambda o: o["unit"]["case"].update(terms_confirmed=False), "Confirm"),
    ],
)
def test_invalid_inactive_unit_profile_is_rejected_before_sampling(edit, match):
    data = case().model_dump(mode="json")
    data["dimensions"][1]["locked_choice"] = "cash"
    edit(data["sleeve_opportunities"][1])
    with pytest.raises(ValueError, match=match):
        validate(PolicySearch.model_validate(data))


@pytest.mark.parametrize(
    "edit,match",
    [
        (
            lambda d: d["sleeve_opportunities"][1].update(id="new_margin"),
            "identifiers must be unique",
        ),
        (lambda d: d["sleeve_opportunities"][0].update(maximum_units=1), "within bounds"),
        (lambda d: d.update(sleeve_opportunities=[]), "within bounds"),
        (
            lambda d: d["sleeve_opportunities"][0].update(minimum_units=2, maximum_units=1),
            "Minimum purchase",
        ),
    ],
)
def test_duplicate_offers_and_out_of_bound_inactive_choices_cannot_hide_behind_locks(edit, match):
    data = case().model_dump(mode="json")
    data["dimensions"][1]["locked_choice"] = "cash"
    edit(data)
    with pytest.raises(ValueError, match=match):
        validate(PolicySearch.model_validate(data))


def test_two_dimensions_cannot_spend_for_the_same_opportunity():
    profile = changed(
        case(), lambda d: d["dimensions"].append(dict(d["dimensions"][1], id="duplicate"))
    )
    with pytest.raises(ValueError, match="same policy"):
        validate(profile)
