"""Original factor scenarios fund QOF calls through actual month-end stock sales."""

from datetime import date
from math import cos, sin

from wealthlab.household.calendar import months
from wealthlab.household.scenario import Scenario
from wealthlab.markets.example import asset
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.stresses import events
from wealthlab.products.qoz_example import synthetic as native


def synthetic(mode="deterministic", stress="early_crash"):
    scenario = policy_source(native())
    return scenario, market_case(scenario, mode, stress), binding()


def policy_source(scenario):
    data = scenario.model_dump(mode="json")
    linked = data["lot_plan"]
    first = data["qoz_plan"]["calls"][0]
    linked["case"]["trades"] = []
    linked["case"]["sale_policies"] = [
        dict(
            id=first["source_trade_id"],
            provenance="illustration",
            date=first["date"],
            account_id="brokerage",
            security_id="stock",
            mode="sell_all",
            prices=linked["opening_prices"],
            commission="0",
            selection="hifo",
        )
    ]
    data["name"] = "Synthetic QOZ shared factors and actual source policy sale"
    return Scenario.model_validate(data)


def binding():
    return HouseholdBinding.model_validate(
        dict(
            securities=[
                dict(
                    security_id="stock",
                    factor="source_stock",
                    federal_cash_character="dividends",
                    nj_cash_character="dividends",
                )
            ],
            qoz=dict(
                account_id="qoz",
                factor="qof_assets",
                return_source_description=(
                    "Original hypothetical net entity-tax asset factor; "
                    "no QOF quotes or performance history"
                ),
                net_entity_tax_pre_investor_cost_confirmed=True,
                replace_dated_asset_returns_confirmed=True,
            ),
            cash_yield_timing="opening_value_received_before_month_end_sales",
            ordinary_cash_character_confirmed=True,
            other_accounts_unmodeled_returns_confirmed=True,
        )
    )


def market_case(scenario, mode, stress):
    data = dict(
        start=scenario.start,
        end=scenario.end,
        mode="deterministic" if mode == "stress" else mode,
        assets=[
            asset("source_stock", "equity", 0.05, 0.18, 0),
            asset("qof_assets", "other", 0.06, 0.15, 0),
        ],
        return_convention="price_plus_cash",
        expected_annual_inflation=0.025,
        annual_inflation_volatility=0.015,
        correlation=[[1, 0.25, 0], [0.25, 1, 0], [0, 0, 1]],
        seed=42,
        paths=4 if mode == "monte_carlo" else 1,
    )
    if mode == "historical":
        data["historical"] = invented_factors(len(list(months(scenario.start, scenario.end))))
    elif mode == "stress":
        data.update(mode="stress", shocks=events(MarketCase.model_validate(data), stress))
    return MarketCase.model_validate(data)


def invented_factors(count):
    # Synthetic input exercises historical replay, not observed QOF/market data.
    return dict(
        source="Original invented mathematical factor scenarios; no actual market or QOF history",
        synthetic=True,
        retrieved_on="2026-10-25",
        available_as_of=date(2000 + count // 12, count % 12 + 1, 1),
        months=[
            dict(
                date=date(2000 + index // 12, index % 12 + 1, 1),
                mark_returns=dict(
                    source_stock=0.004 + 0.02 * sin(index), qof_assets=0.003 + 0.01 * cos(index)
                ),
                cash_yields=dict(source_stock=0, qof_assets=0),
                inflation=0.002,
            )
            for index in range(count)
        ],
    )
