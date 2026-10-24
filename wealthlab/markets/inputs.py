"""Decimal rates, annualized volatility and explicit historical conventions.

A rate of 0.05 means five percent, never five. Mark return and cash yield are
separate assumptions; reinvested total-return marks require zero cash yield.
Expected annual mark return is arithmetic, while volatility describes annual
log returns. Correlation order follows the asset list with inflation last.
Historical observations describe whole months and their actual availability.
Named stress rates multiply a month's growth factor rather than subtracting
percentage points; a lock prevents liquidity without deleting market value.
"""

from datetime import date
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Identifier, Record
from wealthlab.tax.facts import TaxModel

Rate = Annotated[float, Field(ge=-1, le=10)]


class MarketAsset(Record):
    """An assumed risk factor, not a household account or security holding."""

    role: Literal["equity", "bond", "cash", "employer", "other"]
    expected_annual_mark_return: float = Field(gt=-1, le=3)
    annual_volatility: float = Field(ge=0, le=3)
    annual_cash_yield: float = Field(ge=0, le=1)


class HistoricalMonth(TaxModel):
    date: date
    mark_returns: dict[Identifier, Rate]
    cash_yields: dict[Identifier, Annotated[float, Field(ge=0, le=1)]]
    inflation: float = Field(gt=-1, le=1)


class HistoricalData(TaxModel):
    source: str = Field(min_length=1, max_length=500)
    retrieved_on: date
    available_as_of: date
    synthetic: bool
    months: list[HistoricalMonth] = Field(min_length=1)


class MarketShock(TaxModel):
    """A dated scenario overlay with no estimated event probability."""

    name: str = Field(min_length=1, max_length=100)
    month: int = Field(ge=0)
    mark_shocks: dict[Identifier, Rate] = Field(default_factory=dict)
    inflation_override: float | None = Field(default=None, gt=-1, le=1)
    lock_months: dict[Identifier, Annotated[int, Field(ge=1, le=1200)]] = Field(
        default_factory=dict
    )


class MarketCase(TaxModel):
    start: date
    end: date
    mode: Literal["deterministic", "historical", "monte_carlo", "stress"]
    stress_base: Literal["deterministic", "monte_carlo"] = "deterministic"
    assets: list[MarketAsset] = Field(min_length=1, max_length=16)
    return_convention: Literal["price_plus_cash", "total_return_reinvested"]
    expected_annual_inflation: float = Field(gt=-1, le=1)
    annual_inflation_volatility: float = Field(ge=0, le=1)
    correlation: list[list[float]]
    seed: int = Field(ge=0, le=2**64 - 1)
    paths: int = Field(ge=1, le=5000)
    historical: HistoricalData | None = None
    shocks: list[MarketShock] = Field(default_factory=list)

    @model_validator(mode="after")
    def references(self) -> Self:
        from wealthlab.markets.validation import validate

        validate(self)
        return self

    @property
    def stochastic(self):
        return self.mode == "monte_carlo" or (
            self.mode == "stress" and self.stress_base == "monte_carlo"
        )
