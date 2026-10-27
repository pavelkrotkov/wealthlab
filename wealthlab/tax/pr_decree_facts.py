"""The native annual PR comparison reexports its unchanged decree/gain fact contracts."""

from decimal import Decimal

from pydantic import Field

from wealthlab.household.records import Money
from wealthlab.tax.facts import TaxModel
from wealthlab.tax.pr_decree_terms import Decree, MarketableGain
from wealthlab.tax.pr_facts import PRCase
from wealthlab.tax.pr_residence_facts import Claim


class PRComparison(TaxModel):
    annual: PRCase
    decree: Decree = Field(default_factory=Decree)
    gains: list[MarketableGain] = Field(default_factory=list)
    description: str = "Original synthetic conditional decree comparison"
    other_preferential_entitlement: Claim = "unset"
    prior_abt_credit: Money = Decimal(0)
