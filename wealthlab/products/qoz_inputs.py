"""Conditional direct-stock/QOF C-corporation profile; sponsor terms are supplied."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Money, Record
from wealthlab.portfolio.models import Quantity
from wealthlab.products.long_short_inputs import LongShortCase, Rate
from wealthlab.tax.facts import TaxModel

Treatment = Literal["unconfirmed", "denied", "deferred", "allowed"]


class QOZCall(Record):
    date: date
    amount: Annotated[Money, Field(gt=0)]
    source_trade_id: Identifier
    source_lot_id: Identifier
    recapitalization_units: Quantity | None = None
    recapitalization_terms_assumed_confirmed: bool = False


class QOZObservation(Record):
    date: date
    # Net of entity-level taxes, before the separately modeled investor costs.
    asset_return: Annotated[Decimal, Field(ge=-1, le=10)]
    dividend_fraction_of_nav: Rate = Decimal(0)
    locked: bool = False


class QOZPlan(TaxModel):
    account_id: Identifier
    profile: Literal["direct_stock_gain_qof_c_corporation"]
    federal: Treatment = "unconfirmed"
    new_jersey: Treatment = "unconfirmed"
    new_jersey_regime_and_basis_assumed_confirmed: bool
    rural_30_percent_assumed_confirmed: bool = False
    unrelated_direct_gains_no_other_elections_assumed_confirmed: bool
    nonqualified_ep_dividends_no_extraordinary_distributions_assumed_confirmed: bool
    limited_liability_internal_debt_only_assumed_confirmed: bool
    calls_are_optional_partial_subscriptions_assumed_confirmed: bool
    nav_priced_common_stock_retarget_on_calls_assumed_confirmed: bool
    entity_tax_already_in_returns_assumed_confirmed: bool
    source_and_product_tax_excluded_elsewhere_assumed_confirmed: bool
    terms_source_description: str = Field(min_length=1, max_length=500)
    economics: LongShortCase
    preferred_hurdle: Rate
    carry_fraction: Rate
    calls: list[QOZCall] = Field(min_length=1)
    observations: list[QOZObservation] = Field(min_length=1)
    sale_requested: date
    sale_not_before: date
    settlement_months: int = Field(ge=0, le=60)
    mode: Literal["fund", "liquid_reference"] = "fund"
