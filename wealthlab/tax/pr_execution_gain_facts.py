"""Stable source/trade identity connects native PR gain facts to actual household disposals."""

from decimal import Decimal
from typing import Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Money
from wealthlab.tax.facts import TaxModel
from wealthlab.tax.pr_decree_terms import Decree, MarketableGain
from wealthlab.tax.pr_residence_facts import Claim


class PRLinkedGain(TaxModel):
    owner_id: Identifier
    source_id: Identifier
    sale_trade_id: Identifier
    facts: MarketableGain


class PRGainProfile(TaxModel):
    treatment: Literal["ordinary", "incentive", "unresolved"] = "unresolved"
    local_us_credit_treatment: Literal["allowed", "denied", "unresolved"] = "unresolved"
    decree: Decree = Field(default_factory=Decree)
    gains: list[PRLinkedGain] = Field(default_factory=list)
    other_preferential_entitlement: Claim = "unset"
    prior_abt_credit: Money = Decimal(0)
    compliance_expense_id: Identifier | None = None
    source: str = Field(min_length=1, max_length=500)
