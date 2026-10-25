"""Dated synthetic option terms; tax status and broker contracts are never inferred."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Money, Record
from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.models import Price
from wealthlab.tax.facts import TaxModel


class OptionLeg(Record):
    underlying: Literal["STOCK", "INDEX"]
    kind: Literal["call", "put"]
    side: Literal["long", "short"]
    contracts: int = Field(gt=0, le=100000)
    multiplier: int = Field(gt=0, le=100000)
    strike: Price
    opened: date
    expiry: date
    premium: Money
    opening_fee: Money
    closing_fee: Money
    style: Literal["european", "american"]
    settlement: Literal["cash", "physical"]
    expiry_rule: Literal["exercise_if_itm", "lapse"]
    rolls_to: Identifier | None = None
    federal_class: Literal["unresolved", "capital", "section1256"] = "unresolved"
    federal_character: Literal["short_term", "long_term"] = "short_term"


class OptionMark(TaxModel):
    date: date
    stock: Price
    index: Price
    rate: float = Field(ge=-0.1, le=1)
    stock_vol: float = Field(gt=0, le=5)
    index_vol: float = Field(gt=0, le=5)
    stock_yield: float = Field(ge=0, le=1)
    index_yield: float = Field(ge=0, le=1)
    source: str = Field(min_length=1, max_length=200)


class OptionEvent(TaxModel):
    leg_id: Identifier
    date: date
    action: Literal["close", "exercise", "expire"]
    close_price: Money | None = None


class OptionDividend(TaxModel):
    ex_date: date
    pay_date: date
    per_share: Money


class OptionTax(TaxModel):
    federal_rules: Literal["unresolved", "conditional_capital"] = "unresolved"
    nj_rules: Literal["unresolved", "conditional_realized_capital"] = "unresolved"
    straddle: Literal["unresolved", "assume_not_applicable", "supplied_deferrals"] = "unresolved"
    covered_call: Literal["unresolved", "assume_qualified", "assume_not_applicable"] = "unresolved"
    constructive_sale: Literal["unresolved", "assume_not_applicable"] = "unresolved"
    holding_period: Literal["unresolved", "supplied_unaffected"] = "unresolved"
    federal_deferrals: dict[str, Money] = Field(default_factory=dict)
    nj_deferrals: dict[str, Money] = Field(default_factory=dict)
    # Key is a recognition ID, not a claim that NJ follows federal option rules.
    nj_premium_basis: Literal["unresolved", "assume_same_mechanics"] = "unresolved"


class OptionCase(TaxModel):
    holdings: LotCase
    legs: list[OptionLeg] = Field(min_length=1)
    marks: list[OptionMark] = Field(min_length=2)
    events: list[OptionEvent] = Field(default_factory=list)
    dividends: list[OptionDividend] = Field(default_factory=list)
    tax: OptionTax = Field(default_factory=OptionTax)
    outside_cash: Money
    settlement_loan_annual_rate: float = Field(ge=0, le=1)
    allow_settlement_loan: bool
    short_collateral_fraction: Annotated[Decimal, Field(ge=0, le=2)]
    cover_stock_calls: bool
    cash_secure_puts: bool
    stock_sale_fee: Money
    unwind: bool
