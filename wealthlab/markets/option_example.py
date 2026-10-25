"""Original option policies on one shared realized stock/index path, never quote history."""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.example import asset, invented_history
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.stresses import events
from wealthlab.products.option_example import synthetic as contracts
from wealthlab.products.option_household_example import synthetic as household


def synthetic(mode="deterministic", stress="early_crash", strategy="Four-leg synthetic exposure"):
    data = household().model_dump(mode="json")
    data["name"] = "Synthetic model-priced options on realized paths"
    data["accounts"][0]["balance"] = "20000"
    case = data["option_plan"]["case"]
    case["legs"] = contracts(strategy).model_dump(mode="json")["legs"]
    for leg in case["legs"]:
        leg.update(opened=data["start"], expiry="2026-12-31", opening_fee="0", closing_fee="0")
    case["tax"].update(covered_call="assume_not_applicable", straddle="supplied_deferrals")
    scenario = Scenario.model_validate(data)
    market = market_case(mode, stress)
    binding = HouseholdBinding.model_validate(
        dict(
            options=dict(
                account_id="options",
                stock_factor="stock",
                index_factor="index",
                rate=0.04,
                stock_vol=0.2,
                index_vol=0.2,
                stock_yield=0,
                index_yield=0,
                replace_dated_marks_confirmed=True,
                hypothetical_model_execution_confirmed=True,
            ),
            cash_yield_timing="opening_value_received_before_month_end_sales",
            ordinary_cash_character_confirmed=True,
            other_accounts_unmodeled_returns_confirmed=True,
        )
    )
    return scenario, market, binding


def market_case(mode, stress):
    data = dict(
        start="2026-01-01",
        end="2027-01-01",
        mode="deterministic",
        assets=[asset("stock", "equity", 0.05, 0.3, 0), asset("index", "equity", 0.04, 0.18, 0)],
        return_convention="price_plus_cash",
        expected_annual_inflation=0,
        annual_inflation_volatility=0,
        correlation=[[1, 0.5, 0], [0.5, 1, 0], [0, 0, 1]],
        seed=42,
        paths=4 if mode == "monte_carlo" else 1,
    )
    if mode == "historical":
        history = invented_history()
        history.update(
            retrieved_on="2010-01-01", source="Invented underlying paths; not option quote history"
        )
        history["months"] = [
            dict(
                row,
                mark_returns=dict(
                    stock=row["mark_returns"]["employer"], index=row["mark_returns"]["equities"]
                ),
                cash_yields=dict(stock=0, index=0),
            )
            for row in history["months"][:12]
        ]
        data.update(mode=mode, historical=history)
    elif mode == "stress":
        data.update(mode=mode, shocks=events(MarketCase.model_validate(data), stress))
    else:
        data["mode"] = mode
    return MarketCase.model_validate(data)
