"""Editable alternative bindings may change a policy, never the shared market batch."""

import json

import pytest
from employer_market_cases import flat

from wealthlab.ui.market_household import paired_inputs


@pytest.mark.parametrize("bundle", [False, True])
def test_existing_household_and_optional_policy_bundle_are_supported(bundle):
    household, _, binding = flat()
    data = household.model_dump(mode="json")
    if bundle:
        terms = binding.model_dump(mode="json")
        terms["employers"][0]["employment"] = None
        data = dict(household=data, binding=terms)
    other, policy = paired_inputs(json.dumps(data), binding)
    assert other == household
    assert (policy.employers[0].employment is None) == bundle


def test_paired_policy_cannot_override_the_shared_market():
    household, market, binding = flat()
    data = dict(household=household.model_dump(mode="json"), market=market.model_dump(mode="json"))
    with pytest.raises(ValueError, match="batch stays shared"):
        paired_inputs(json.dumps(data), binding)
