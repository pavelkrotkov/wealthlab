"""Every offered unit needs supported dated execution on all named market checks.

Known wash groups and ownership roles are factual input, independent of whether
an offer happens to make a gain on one simulated path. No cross-book wash
engine or intramonth option settlement is inferred from zero-unit controls.
"""

from copy import deepcopy

import pytest
from optimization_cases import changed
from optimization_option_cases import case
from test_policy_option_allocation_guards import locked

from wealthlab.optimization.option_allocation_example import extend
from wealthlab.optimization.option_offer_validation import validate_owner
from wealthlab.optimization.validation import validate


def test_offer_validates_a_named_stress_even_when_its_only_active_quantity_is_zero():
    def edit(data):
        check = deepcopy(data["training"])
        check.update(
            mode="stress",
            paths=1,
            shocks=[dict(name="locked", month=0, lock_months=dict(option_stock=1))],
        )
        data["robustness"] = dict(locked=dict(market=check, required=False))

    with pytest.raises(ValueError, match="liquidity locks"):
        validate(locked(edit))


def test_zero_units_cannot_hide_generated_underlying_dividend_yields():
    def edit(data):
        for market in (data["training"], data["validation"]):
            next(a for a in market["assets"] if a["id"] == "option_stock")["annual_cash_yield"] = (
                0.01
            )

    with pytest.raises(ValueError, match="zero generated cash yield"):
        validate(locked(edit))


def test_option_purchase_rejects_a_known_wash_group_shared_with_the_actual_lot_book():
    def edit(data):
        group = data["household"]["lot_plan"]["case"]["securities"][0]["wash_group"]
        data["option_opportunity"]["unit"]["case"]["holdings"]["securities"][0]["wash_group"] = (
            group
        )

    with pytest.raises(ValueError, match="distinct wash groups"):
        validate(locked(edit))


def test_native_roles_map_to_actual_member_ids_and_explicit_joint_ownership():
    profile = case()
    item = profile.option_opportunity
    assert item is not None
    data = item.model_dump(mode="json")
    data["unit"]["case"]["holdings"]["accounts"][0]["owner"] = "spouse"
    data["owner"] = profile.household.members[1].id
    validate_owner(profile.household, type(item).model_validate(data))
    validate_owner(profile.household, item)


def test_the_synthetic_starter_preserves_existing_plans_and_private_inputs():
    with pytest.raises(ValueError, match="existing option book or opportunity"):
        extend(case())
    profile = changed(case(), lambda d: d["household"].update(synthetic=False))
    with pytest.raises(ValueError, match="only extends synthetic"):
        extend(profile)


def test_option_factor_mapping_must_refer_to_its_actual_destination_account():
    profile = locked(lambda d: d["option_opportunity"]["binding"].update(account_id="elsewhere"))
    with pytest.raises(ValueError, match="actual option account"):
        validate(profile)
