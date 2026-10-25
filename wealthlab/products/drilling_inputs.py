"""Debt-free synthetic cash-basis drilling terms with independently supplied tax limitations."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Money, Record
from wealthlab.products.loss_timing import LossTiming
from wealthlab.tax.facts import FederalIncome, TaxModel

Units = Annotated[Decimal, Field(ge=0, max_digits=18, decimal_places=6)]
Rate = Annotated[Decimal, Field(ge=0, le=1, decimal_places=12)]


class DrillingLimits(TaxModel):
    basis: Money
    at_risk: Money
    passive: Money
    other: Money


class DrillingDeduction(Record):
    component: Literal["idc", "depletion", "depreciation", "operating_loss"]
    federal_requested: Money
    nj_requested: Money
    federal_limits: DrillingLimits
    nj_limits: DrillingLimits
    federal_timing: LossTiming
    nj_timing: LossTiming
    federal_basis_reduction: Money
    nj_basis_reduction: Money
    at_risk_reduction: Money


class DrillingObservation(Record):
    date: date
    production_units: Units
    commodity_price: Money
    royalty_fraction: Rate
    capital_call: Money
    operating_cost: Money
    idc_cost: Money
    tangible_cost: Money
    manager_fee: Money
    liability_cost: Money
    residual_property_value: Money
    distribution_request: Money
    deductions: list[DrillingDeduction]
    supplemental_federal: FederalIncome
    exit_requested: bool
    exit_gross_proceeds: Money
    exit_fee: Money
    reference_price: Annotated[Decimal, Field(gt=0, max_digits=18, decimal_places=8)]
    reference_cash_request: Money
    reference_locked: bool


class DrillingPlan(TaxModel):
    account_id: Identifier
    legal_form: Literal["unconfirmed", "general_partner", "limited_partner"]
    federal_ordinary: Literal["unconfirmed", "nonpassive_assumption", "passive_assumption"]
    ordinary_nonsection1411_classification_supplied_confirmed: bool = False
    working_interest_eligibility_supplied_confirmed: bool
    se_classification: Literal[
        "unconfirmed", "supplied_box14", "zero_under_supplied_classification"
    ]
    se_classification_basis: str = Field(min_length=10, max_length=500)
    supplied_qbi_amt_history_and_limits_confirmed: bool
    full_tax_optimization_supported: Literal[False] = False
    all_cash_basis_terms_and_recognition_complete_confirmed: bool
    paid_operating_costs_deductible_assumption_confirmed: bool
    other_tax_inputs_exclude_product_confirmed: bool
    household_recourse_for_modeled_creditors: bool
    unmodeled_liability_risk_acknowledged: bool
    opening_cash: Money
    opening_property_value: Money
    opening_federal_basis: Money
    opening_nj_basis: Money
    opening_at_risk: Money
    opening_federal_tangible_basis: Money = Decimal(0)
    opening_nj_tangible_basis: Money = Decimal(0)
    opening_reference_price: Annotated[Decimal, Field(gt=0)]
    federal_recapture_limit: Money
    nj_recapture_limit: Money
    nj_exit_category: Literal["partnership", "dispositions", "unconfirmed"]
    residual_capital_niit_inclusion_assumed_confirmed: bool
    residual_federal_capital_character: Literal["short_term", "long_term", "unconfirmed"] = (
        "unconfirmed"
    )
    federal_exit_loss_limits: DrillingLimits
    nj_exit_loss_limits: DrillingLimits
    federal_exit_loss_timing: LossTiming
    nj_exit_loss_timing: LossTiming
    reference_nj_wash_treatment: Literal["unconfirmed", "no_wash_assumption", "federal_rules"] = (
        "unconfirmed"
    )
    reference_zero_fees_and_no_external_identical_trades_confirmed: bool
    observations: list[DrillingObservation] = Field(min_length=1)
    mode: Literal["drilling", "liquid_reference"] = "drilling"
