"""Original account ownership and known offers remain authoritative at both API boundaries."""

import pytest
from optimization_qoz_cases import case, changed

from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.inputs import PolicyChoice
from wealthlab.optimization.qoz_controls import apply, validate
from wealthlab.optimization.qoz_profiles import validate_native


def test_duplicate_offer_ids_and_unknown_or_duplicate_controllers_fail_before_projection():
    with pytest.raises(ValueError, match="identifiers"):
        validate(changed(case(), lambda d: d["qoz_offers"].append(d["qoz_offers"][0])))
    with pytest.raises(ValueError, match="complete supplied"):
        validate(
            changed(case(), lambda d: d["dimensions"][0]["choices"][0].update(qoz_offer="missing"))
        )
    profile = case()
    with pytest.raises(ValueError, match="Only one dimension"):
        compile_candidate(
            profile, [profile.dimensions[0].choices[0], profile.dimensions[0].choices[1]]
        )


def test_offers_require_original_zero_opening_plan_and_real_tax_ledger():
    with pytest.raises(ValueError, match="original native"):
        validate(changed(case(), lambda d: d["household"].update(qoz_plan=None)))
    with pytest.raises(ValueError, match="explicit native"):
        validate_native(case().household.model_copy(update={"tax_plan": None}))


def test_uncontrolled_plan_is_preserved_but_direct_unknown_or_capital_rewrites_are_rejected():
    profile = case()
    household, _ = compile_candidate(profile, [])
    assert household.qoz_plan == profile.household.qoz_plan
    data = profile.household.model_dump(mode="json")
    binding = profile.binding.model_dump(mode="json")
    with pytest.raises(ValueError, match="known QOZ"):
        apply(data, binding, profile, [PolicyChoice(id="invalid", qoz_offer="missing")])
    data["accounts"][-1]["owner"] = "person_b"
    with pytest.raises(ValueError, match="original household account"):
        apply(data, binding, profile, [profile.dimensions[0].choices[0]])
