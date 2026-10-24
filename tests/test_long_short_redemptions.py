"""Redemptions conserve capital, and a lock leaves the supplied request unpaid."""

import pytest
from long_short_cases import batch, flat

from wealthlab.markets.inputs import MarketCase
from wealthlab.products.long_short_run import run


@pytest.mark.parametrize("locked", [False, True])
def test_redemption_cash_moves_once_without_erasing_unpaid_requests(locked):
    case, market = flat(
        exit_at_horizon=False,
        redemptions=[dict(id="draw", provenance="assumption", date="2026-01-31", amount=20000)],
    )
    data = market.model_dump(mode="json")
    if locked:
        data.update(mode="stress", shocks=[dict(name="lock", month=0, lock_months=dict(long=1))])
    row = run(case, batch(MarketCase.model_validate(data)))["details"][0]["rows"][0]
    assert row["redemption_paid"] == (0 if locked else 20000)
    assert row["redemption_unfilled"] == (20000 if locked else 0)
    assert row["investor_wealth"] == 110000
    assert row["outside_cash"] == (10000 if locked else 30000)
