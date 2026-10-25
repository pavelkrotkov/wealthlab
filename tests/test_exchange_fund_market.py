"""Identical realized prices drive both policies without inferring taxable yield.

The independent one-year 12% check permits only the stated decimal precision.
Total-return reinvestment and numerically zero prices are rejected because the
adapter has no hidden dividend or terminal-write-off tax classification.
"""

from dataclasses import replace
from datetime import date
from decimal import Decimal

import numpy as np
import pytest
from exchange_fund_cases import flat

from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate
from wealthlab.products.exchange_fund_compare import compare
from wealthlab.products.exchange_fund_market import bind


def market(case):
    ids = list(case.exchange_fund_plan.opening_prices)
    return MarketCase(
        start=case.start,
        end=case.end,
        mode="deterministic",
        seed=42,
        paths=1,
        assets=[
            dict(
                id=identity,
                provenance="illustration",
                role="equity",
                expected_annual_mark_return=0.12,
                annual_volatility=0,
                annual_cash_yield=0,
            )
            for identity in ids
        ],
        return_convention="price_plus_cash",
        expected_annual_inflation=0,
        annual_inflation_volatility=0,
        correlation=np.eye(4).tolist(),
    )


def test_one_realized_path_gives_same_before_fee_terminal_gain_without_mutating_sources():
    scenario = flat()
    source = scenario.model_dump_json()
    batch = generate(market(scenario))
    bound = bind(scenario, batch)
    assert abs(bound.exchange_fund_plan.observations[-1].prices["diversified_a"] - 112) < (
        Decimal(".000001")
    )
    result = compare(bound)
    assert abs(
        result["outcomes"]["exchange"]["net_wealth"]
        - (result["outcomes"]["direct_sale"]["net_wealth"])
    ) <= Decimal(".01")
    assert scenario.model_dump_json() == source
    assert batch.metadata["input"]["seed"] == 42


@pytest.mark.parametrize(
    "field,value,message",
    [
        ("cash_yields", 0.01, "zero cash"),
        ("mark_returns", -1, "above complete"),
        ("mark_returns", float("nan"), "finite"),
    ],
)
def test_unsupported_path_economics_are_rejected(field, value, message):
    scenario = flat()
    batch = generate(market(scenario))
    batch = replace(batch, **{field: np.full_like(getattr(batch, field), value)})
    with pytest.raises(ValueError, match=message):
        bind(scenario, batch)


def test_missing_horizon_and_selected_path_block():
    scenario = flat()
    batch = generate(market(scenario))
    with pytest.raises(ValueError, match="selected path"):
        bind(scenario, batch, 1)
    with pytest.raises(ValueError, match="horizon"):
        bind(scenario.model_copy(update={"end": date(2028, 1, 1)}), batch)


def test_reinvested_total_returns_and_rounding_to_zero_are_rejected():
    scenario = flat()
    case = market(scenario).model_copy(update={"return_convention": "total_return_reinvested"})
    with pytest.raises(ValueError, match="price-only"):
        bind(scenario, generate(case))
    batch = generate(market(scenario))
    tiny = np.full_like(batch.mark_returns, np.nextafter(-1.0, 0.0))
    with pytest.raises(ValueError, match="rounded to zero"):
        bind(scenario, replace(batch, mark_returns=tiny))
