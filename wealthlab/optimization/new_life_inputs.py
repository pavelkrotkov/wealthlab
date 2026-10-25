"""Whole supplied new-issue quotes name the owner and independent terms explicitly."""

from pydantic import Field

from wealthlab.household.records import Identifier, Record
from wealthlab.products.life_household_inputs import LifeHolding


class NewLifeOffer(Record):
    owner: Identifier
    holding: LifeHolding
    matched_new_issue_terms_confirmed: bool = False
    source: str = Field(min_length=10, max_length=1000)
