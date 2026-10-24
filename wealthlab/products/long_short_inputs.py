"""A supplied monthly margin model, without inferred broker rights or tax deductions."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Money, Record
from wealthlab.tax.facts import TaxModel

Rate = Annotated[Decimal, Field(ge=0, le=1, decimal_places=8)]
Multiple = Annotated[Decimal, Field(ge=0, le=5, decimal_places=6)]


class Redemption(Record):
    date: date
    amount: Money


class LongShortCase(TaxModel):
    opening_equity: Annotated[Decimal, Field(gt=0, max_digits=18, decimal_places=2)]
    outside_cash: Money
    long_factor: Identifier
    short_factor: Identifier
    long_multiple: Multiple
    short_multiple: Multiple
    annual_borrow_rate: Rate
    annual_financing_rate: Rate
    annual_manager_fee: Rate
    turnover_cost: Rate
    exit_cost: Rate
    maintenance_fraction_of_gross: Rate
    rebalance: Literal["none", "monthly", "quarterly", "annually"]
    margin_policy: Literal["liquidate_on_breach", "top_up_then_liquidate"]
    recourse: Literal["full_margin_account_liability"]
    short_proceeds: Literal["segregated_no_interest_no_reuse"]
    timing: Literal["opening_notional_costs_month_end_marks_then_margin_redemptions_rebalance"]
    exit_at_horizon: bool
    terms_confirmed: bool
    redemptions: list[Redemption] = Field(default_factory=list)
