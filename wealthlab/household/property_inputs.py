"""Conditional USD personal-home marks and monthly cash closings, never inferred tax eligibility."""

from datetime import date
from typing import Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Money, Record
from wealthlab.tax.facts import TaxModel


class PropertyObservation(Record):
    date: date
    available_on: date
    value: Money
    locked: bool


class PropertySale(Record):
    date: date
    gross_proceeds: Money
    closing_costs: Money
    maximum_owner_cash_to_close: Money
    federal_taxable_gain: Money
    federal_character: Literal["short_term", "long_term", "unconfirmed"]
    nj_taxable_gain: Money
    costs_due_only_on_executed_close_confirmed: bool
    no_closing_withholding_or_other_escrow_terms_confirmed: bool
    prelimited_tax_recognition_and_no_deduction_claims_confirmed: bool


class PropertyHolding(Record):
    account_id: Identifier
    source_ref: str = Field(min_length=1, max_length=500)
    source_date: date
    available_on: date
    use: Literal["personal_use_home", "rental_or_business", "unconfirmed"]
    ownership_legal_use_and_tax_facts_supplied_confirmed: bool
    unchanged_basis_and_no_other_asset_cashflows_confirmed: bool
    opening_federal_basis: Money
    opening_nj_basis: Money
    linked_debt_ids: list[Identifier]
    observations: list[PropertyObservation] = Field(min_length=1)
    terminal_action: Literal["retain", "sell"]
    sale: PropertySale | None = None


class PropertyPlan(TaxModel):
    holdings: list[PropertyHolding] = Field(min_length=1)
    other_tax_inputs_exclude_property_recognition_confirmed: bool
    debt_payoff_full_month_native_interest_confirmed: bool
    timing: Literal["month_end_after_required_products_before_advisory_and_optional_saving"]
