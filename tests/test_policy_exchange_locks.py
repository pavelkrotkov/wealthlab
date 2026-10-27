"""A generated liquid market cannot erase a supplied product execution lock.

Ordinary bills can still be fully funded while retained stock or an unsold
basket prevents completed after-tax ranking. Zero NAV alone is insufficient.
"""

import pytest
from optimization_cases import changed
from optimization_exchange_cases import case

from wealthlab.markets.paths import generate
from wealthlab.optimization.search import evaluate


@pytest.mark.parametrize("index", range(4))
def test_entered_terminal_lock_survives_shared_market_compilation_and_blocks_every_exit(index):
    def edit(data):
        data["household"]["exchange_fund_plan"]["observations"][-1]["locked"] = True
        for path in data["exchange_opportunities"]:
            path["plan"]["observations"][-1]["locked"] = True

    profile = changed(case(), edit)
    selection = [profile.dimensions[0].choices[0], profile.dimensions[-1].choices[index]]
    candidate, result = evaluate(profile, selection, index, generate(profile.training))
    final = result["details"][0]["rows"][-1]
    assert not candidate["constraints"]["completed_after_tax_exit"]
    assert candidate["median_real_after_tax_exit_wealth"] is None
    assert candidate["constraints"]["spending_and_product_safety"]
    assert final["closing_cash"] == 251999
    assert final["account_balances"]["exchange"] == 10000
