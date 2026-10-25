"""All shared-market methods execute the actual matched native contract and reference."""

import pytest

from wealthlab.products.drilling_market import compare
from wealthlab.products.drilling_market_example import synthetic


@pytest.mark.parametrize("mode", ["deterministic", "historical", "monte_carlo", "stress"])
def test_price_binding_methods_pair_complete_realized_batches_and_native_audits(mode):
    result = compare(synthetic(mode))
    policies = result["policies"]
    assert {p["batch_id"] for p in policies.values()} == {result["batch"]["metadata"]["batch_id"]}
    expected = 4 if mode == "monte_carlo" else 1
    assert [len(p["outcomes"]) for p in policies.values()] == [expected, expected]
    assert all(
        d["rows"][-1]["drilling_audit"]["terminal_state"]["closed"]
        for d in policies["drilling"]["details"]
    )
    if mode == "stress":
        assert policies["liquid_reference"]["outcomes"][0]["joint_funding_feasible"] is False
    assert result["full_tax_optimization_supported"] is False
