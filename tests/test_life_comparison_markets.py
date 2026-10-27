"""All alternatives consume the same market batch and actual saving share prices."""

from wealthlab.products.life_comparison import compare
from wealthlab.products.life_comparison_markets import synthetic


def test_deterministic_market_growth_changes_actual_saving_value():
    result = compare(synthetic("deterministic"))
    outcome = result["alternatives"]["liquid_term"]["outcomes"][0]
    assert outcome["marked_wealth_after_recognized_tax"] > 6700
    rows = result["alternatives"]["liquid_term"]["details"][0]["rows"]
    prices = [row["trades"][0]["price"] for row in rows[-1]["saving_audit"]]
    assert prices[0] != prices[1]
