"""Synthetic 130/30 sleeve and independently editable unlevered reference on identical paths."""

from wealthlab.markets.example import asset
from wealthlab.markets.household_example import selected_mode
from wealthlab.markets.inputs import MarketCase
from wealthlab.products.long_short_inputs import LongShortCase


def synthetic(mode="deterministic", stress="early_crash"):
    market = MarketCase.model_validate(
        dict(
            start="2026-01-01",
            end="2028-01-01",
            mode="monte_carlo" if mode == "monte_carlo" else "deterministic",
            assets=[
                asset("long", "equity", 0.05, 0.18, 0.02),
                asset("short", "equity", 0.04, 0.22, 0.02),
            ],
            return_convention="price_plus_cash",
            expected_annual_inflation=0.025,
            annual_inflation_volatility=0.015,
            correlation=[[1, 0.8, 0.1], [0.8, 1, 0.1], [0.1, 0.1, 1]],
            seed=42,
            paths=100 if mode == "monte_carlo" else 1,
        )
    )
    if mode == "historical":
        market = historical(market)
    elif mode == "stress":
        if stress == "short_squeeze":
            data = market.model_dump(mode="json")
            data.update(
                mode="stress", shocks=[dict(name=stress, month=0, mark_shocks=dict(short=4))]
            )
            market = MarketCase.model_validate(data)
        else:
            market = selected_mode(market, mode, stress)
    sleeve = terms()
    reference = LongShortCase.model_validate(
        dict(
            sleeve.model_dump(),
            long_multiple=1,
            short_multiple=0,
            annual_manager_fee=".0005",
            maintenance_fraction_of_gross=1,
        )
    )
    return dict(
        market=market.model_dump(mode="json"),
        sleeve=sleeve.model_dump(mode="json"),
        reference=reference.model_dump(mode="json"),
    )


def terms():
    return LongShortCase.model_validate(
        dict(
            opening_equity="100000",
            outside_cash="10000",
            long_factor="long",
            short_factor="short",
            long_multiple="1.3",
            short_multiple=".3",
            annual_borrow_rate=".02",
            annual_financing_rate=".06",
            annual_manager_fee=".01",
            turnover_cost=".001",
            exit_cost=".001",
            maintenance_fraction_of_gross=".25",
            rebalance="monthly",
            margin_policy="top_up_then_liquidate",
            recourse="full_margin_account_liability",
            short_proceeds="segregated_no_interest_no_reuse",
            timing="opening_notional_costs_month_end_marks_then_margin_redemptions_rebalance",
            exit_at_horizon=True,
            terms_confirmed=True,
        )
    )


def historical(case):
    from wealthlab.markets.household_example import synthetic as previous

    _, other, _ = previous("historical")
    history = other.historical.model_dump(mode="json")
    for row in history["months"]:
        rate, cash = row["mark_returns"]["equities"], row["cash_yields"]["equities"]
        row["mark_returns"], row["cash_yields"] = (
            dict(long=rate, short=rate),
            dict(long=cash, short=cash),
        )
    return MarketCase.model_validate(
        dict(case.model_dump(mode="json"), mode="historical", historical=history)
    )
