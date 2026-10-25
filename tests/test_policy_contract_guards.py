"""Opaque issuer inventory and missing factor/contract plans retain explicit constraints."""

import pytest
from optimization_cases import changed
from optimization_contract_cases import case

from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.contract_example import extend
from wealthlab.optimization.search import search


@pytest.mark.parametrize(
    "field,value,match", [("options", None, "stock/index"), ("employers", [], "every employer")]
)
def test_every_contract_account_requires_its_native_market_binding(field, value, match):
    profile = changed(case(), lambda d: d["binding"].update({field: value}))
    with pytest.raises(ValueError, match=match):
        compile_candidate(profile, [])


def test_an_employer_account_cannot_drop_its_contract_plan():
    profile = changed(case(), lambda d: d["household"].update(compensation_plan=None))
    with pytest.raises(ValueError, match="configured compensation_plan"):
        compile_candidate(profile, [])


def test_contract_participation_does_not_silently_waive_the_issuer_inventory_constraint():
    profile = changed(case(), lambda d: d["targets"].update(maximum_issuer_weight="1"))
    result = search(profile)
    assert result["selection"] is None
    assert "issuer_limit" in result["candidates"][0]["unmet_constraints"]


def test_synthetic_starter_never_replaces_existing_contracts_or_adds_assets_to_private_inputs():
    with pytest.raises(ValueError, match="replace existing"):
        extend(case())
    profile = changed(case(), lambda d: d["household"].update(synthetic=False))
    with pytest.raises(ValueError, match="only extends synthetic"):
        extend(profile)
