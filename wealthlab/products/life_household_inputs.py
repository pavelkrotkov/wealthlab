"""A household policy has actual funding, complete dated values and supplied failure exits."""

from datetime import date
from typing import Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Money
from wealthlab.products.life_contract_inputs import LifeContract
from wealthlab.products.life_contract_records import PolicyEvent
from wealthlab.products.life_illustration_records import LifeValue
from wealthlab.tax.facts import TaxModel
from wealthlab.tax.source_withholding import SourceWithholding


class PolicyFailureExit(TaxModel):
    event: PolicyEvent
    source: str = Field(min_length=1, max_length=500)
    applicable_to_unfunded_payment_confirmed: bool
    withholding: SourceWithholding | None = None


class LifeHolding(TaxModel):
    account_id: Identifier
    contract: LifeContract
    opening_values: LifeValue
    funding: Literal["cash_only", "permitted_household_sales"]
    failure_exits: dict[str, PolicyFailureExit]
    withholding: dict[str, SourceWithholding] = Field(default_factory=dict)
    payments_complete_through: date
    other_inputs_exclude_policy_confirmed: bool


class LifeHouseholdPlan(TaxModel):
    holdings: list[LifeHolding] = Field(min_length=1)
    insurance_need_by_owner: dict[Identifier, Money]
