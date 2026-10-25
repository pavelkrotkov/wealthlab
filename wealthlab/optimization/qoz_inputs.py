"""Complete sourced QOF subscriptions retain original source stock and legal assumptions."""

from datetime import date

from pydantic import Field

from wealthlab.household.records import Record
from wealthlab.products.qoz_inputs import QOZPlan


class QOZOffer(Record):
    plan: QOZPlan | None
    source: str = Field(min_length=10, max_length=1000)
    source_date: date
    complete_cash_tax_and_terms_confirmed: bool = False
    profile_valid_for_all_candidate_income_and_paths_confirmed: bool = False
    declined_no_prior_interest_or_obligations_confirmed: bool = False
