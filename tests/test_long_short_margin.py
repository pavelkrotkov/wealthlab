"""Outside capital is finite; locked positions retain liabilities rather than disappearing."""

from long_short_cases import batch, flat

from wealthlab.markets.inputs import MarketCase
from wealthlab.products.long_short_run import run


def squeezed(outside_cash, locked=False):
    case, market = flat(outside_cash=outside_cash, exit_at_horizon=False)
    data = market.model_dump(mode="json")
    shock = dict(name="squeeze", month=0, mark_shocks=dict(short=4))
    if locked:
        shock["lock_months"] = dict(short=1)
    data.update(mode="stress", shocks=[shock])
    return run(case, batch(MarketCase.model_validate(data)))["details"][0]


def test_funded_margin_call_transfers_existing_outside_cash_once():
    result = squeezed(100000)
    row = result["rows"][0]
    assert (row["margin_requested"], row["margin_topup"], row["margin_unfunded"]) == (
        90000,
        90000,
        0,
    )
    assert (row["equity"], row["outside_cash"], row["investor_wealth"]) == (70000, 10000, 80000)
    assert not result["summary"]["margin_failure"]


def test_locked_short_squeeze_cannot_force_a_fictitious_exit():
    result = squeezed(10000, True)
    row = result["rows"][0]
    assert row["margin_exit_blocked"]
    assert not row["closed"]
    assert row["short_liability"] == 150000
    assert row["investor_wealth"] == -10000
    assert result["summary"]["margin_failure"]
