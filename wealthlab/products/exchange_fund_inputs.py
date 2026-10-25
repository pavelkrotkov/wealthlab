"""Conditional synthetic exchange contracts; no sponsor or tax eligibility is inferred."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Money, Record
from wealthlab.portfolio.models import Lot, Price, Quantity, Security
from wealthlab.products.household_inputs import SleeveAllocation
from wealthlab.tax.facts import SignedMoney, TaxModel

Weight = Annotated[Decimal, Field(gt=0, le=1, decimal_places=12)]
Treatment = Literal["unconfirmed", "deferred", "denied"]


class ExchangeBasket(Record):
    security: Security
    value_weight: Weight
    federal_basis_weight: Weight
    nj_basis_weight: Weight
    federal_holding_start: date


class ExchangeObservation(Record):
    date: date
    prices: dict[str, Price]
    distribution: Money = Decimal(0)
    federal_basis_adjustment: SignedMoney = Decimal(0)
    nj_basis_adjustment: SignedMoney = Decimal(0)
    # Separate from cash: caller supplies complete income/fee/basis classification.
    locked: bool = False
    allocation: SleeveAllocation


class ExchangeRequest(Record):
    date: date
    action: Literal["redeem", "sell_liquid"]
    # Only used for an explicitly permitted full early cash redemption.
    early_tax: SleeveAllocation
    early_tax_confirmed: bool = False


class ExchangeFundPlan(TaxModel):
    account_id: Identifier
    nj_wash_treatment: Literal["unconfirmed", "no_wash_assumption", "federal_rules"] = "unconfirmed"
    source_security: Security
    source_lot: Lot
    contribution_quantity: Quantity
    opening_prices: dict[str, Price]
    accepted: bool
    federal_contribution: Treatment = "unconfirmed"
    nj_contribution: Treatment = "unconfirmed"
    federal_basket_distribution: Treatment = "unconfirmed"
    nj_basket_distribution: Treatment = "unconfirmed"
    federal_distribution_character: Literal["short_term", "long_term"]
    liquid_after: date
    early_redemption: Literal["denied", "cash_with_supplied_tax"]
    annual_fee: Decimal = Field(ge=0, le=1)
    early_fee_fraction: Decimal = Field(ge=0, le=1)
    basket: list[ExchangeBasket] = Field(min_length=1)
    observations: list[ExchangeObservation] = Field(min_length=1)
    requests: list[ExchangeRequest] = Field(default_factory=list)
    all_terms_tax_and_basis_assumptions_confirmed: bool
    other_tax_inputs_exclude_product_confirmed: bool
    no_external_substantially_identical_trades_confirmed: bool
    mode: Literal["exchange", "direct_sale"] = "exchange"
