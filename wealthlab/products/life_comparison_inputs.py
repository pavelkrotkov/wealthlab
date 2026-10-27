"""Explicit alternative households share capital, spending, tax and market background."""

from pydantic import Field

from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.inputs import MarketCase
from wealthlab.tax.facts import TaxModel


class LifeComparison(TaxModel):
    alternatives: dict[str, Scenario] = Field(min_length=2, max_length=6)
    liquid_reference: str
    term_account_ids: list[str]
    independently_priced_protection_confirmed: bool
    market: MarketCase | None = None
    binding: HouseholdBinding | None = None
