"""Independent source facts authorize only their exact declared search-input scope."""

from datetime import date
from typing import Literal

from pydantic import Field

from wealthlab.household.records import Record
from wealthlab.products.drilling_inputs import DrillingPlan


class DrillingEnvelope(Record):
    source: str = Field(min_length=10, max_length=1000)
    as_of: date
    valid_through: date
    search_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    all_candidate_employment_income_funding_and_bound_price_paths_confirmed: bool = False
    supplied_legal_se_qbi_amt_history_limits_recapture_release_facts_confirmed: bool = False
    full_tax_optimization_supported: Literal[False] = False


class DrillingOffer(Record):
    plan: DrillingPlan | None
    source: str = Field(min_length=10, max_length=1000)
    source_date: date
    complete_matched_terms_confirmed: bool = False
    mode_change_no_prior_interest_or_obligations_confirmed: bool = False
    declined_no_prior_interest_or_obligations_confirmed: bool = False
