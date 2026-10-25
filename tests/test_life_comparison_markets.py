"""All alternatives consume the same market batch and actual saving share prices."""

import pytest

from wealthlab.products.life_comparison import compare
from wealthlab.products.life_comparison_markets import synthetic


@pytest.mark.parametrize("mode", ["deterministic", "historical", "monte_carlo", "stress"])
def test_shared_market_paths_preserve_cash_and_separate_supplied_policy_values(mode):
    result = compare(synthetic(mode))
    batch = result["batch"]["metadata"]["batch_id"]
    assert all(a["market"]["batch_id"] == batch for a in result["alternatives"].values())
    reference = result["alternatives"]["liquid_term"]
    assert all(o["saving_spent"] == 1800 for o in reference["outcomes"])
    assert all(o["ending_protection_gap"] == 0 for o in reference["outcomes"])
    assert all(
        o["marked_wealth_after_recognized_tax"] == 7000
        for o in result["alternatives"]["limited"]["outcomes"]
    )
    assert len(result["differences"]["limited"]) == len(reference["outcomes"])


def test_deterministic_market_growth_changes_actual_saving_value():
    result = compare(synthetic("deterministic"))
    outcome = result["alternatives"]["liquid_term"]["outcomes"][0]
    assert outcome["marked_wealth_after_recognized_tax"] > 6700
    rows = result["alternatives"]["liquid_term"]["details"][0]["rows"]
    prices = [row["trades"][0]["price"] for row in rows[-1]["saving_audit"]]
    assert prices[0] != prices[1]
