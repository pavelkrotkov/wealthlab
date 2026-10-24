"""Whole-account factor values do not establish underlying issuer inventory."""

from test_employer_market_returns import projection as projection


def test_factor_and_contingent_coverage_are_separate_from_issuer_inventory(projection):
    _, result = projection
    last = result["details"][0]["rows"][-1]
    assert last["market_factor_values"]["employer"] == last["employer_vested"]
    assert (
        last["market_contingent_factor_values"]["employer"] == last["employer_unvested_contingent"]
    )
    assert last["market_max_security_weight"] is None
    assert not last["market_issuer_concentration_complete"]
    assert last["market_unmapped_factor_accounts"] == ["retirement"]


def test_export_retains_original_uncompiled_terms(projection):
    household, result = projection
    assert household.model_dump(mode="json") == result["household"]
    assert all(
        e["kind"] != "net_return" for e in result["household"]["compensation_plan"]["events"]
    )
