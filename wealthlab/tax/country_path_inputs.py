"""Fixed country facts and explicit wage identities remain shared across policy choices.

A binding varies a monthly USD wage amount, never the supplied residence,
source classification, recognition date or dated currency quote. Confirmation
covers the declared candidate/path envelope; it is not legal certification.
"""

from datetime import date

from pydantic import Field

from wealthlab.household.records import Identifier
from wealthlab.tax.facts import TaxModel
from wealthlab.tax.spain_execution_facts import SpainExecution


class CountryWageSource(TaxModel):
    income_id: Identifier
    source_id: Identifier
    date: date


class CountryCashSource(TaxModel):
    annual_id: Identifier
    account_id: Identifier
    asset_id: Identifier


class CountryContext(TaxModel):
    spain: SpainExecution | None = None
    cash_sources: list[CountryCashSource] = Field(default_factory=list, max_length=2000)
    wage_sources: list[CountryWageSource] = Field(default_factory=list, max_length=2000)
    source: str = Field(min_length=1, max_length=1000)
    source_date: date
    valid_through: date
    all_candidate_income_market_and_fiscal_facts_confirmed: bool
    replace_bound_future_wages_confirmed: bool = False
