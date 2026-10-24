"""Ordinary retirement/spouse claims under explicit survival and work-history assumptions."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Identifier, Money, Record
from wealthlab.tax.facts import TaxModel


class SocialPerson(Record):
    birth_date: date
    pia_january_2026: Money
    own_insured: bool
    claim_month: date
    partner: Identifier | None
    spousal_eligibility_confirmed: bool


class SocialCase(TaxModel):
    start_year: int = Field(ge=2026, le=2200)
    end_year: int = Field(ge=2027, le=2201)
    members: list[SocialPerson] = Field(min_length=1, max_length=2)
    no_earnings_test_deductions_confirmed: bool
    no_other_auxiliaries_confirmed: bool
    history_policy: Literal["no_prior_deductions_suspensions_disability_or_restricted_claims"]
    claim_rule_policy: Literal["freeze_current_claim_rules"]
    survival_policy: Literal["all_members_survive_projection"]
    future_cola_assumption: Annotated[Decimal, Field(ge=0, le="0.10", decimal_places=6)]
    payment_policy: Literal["following_month_no_offsets"]

    @model_validator(mode="after")
    def references(self) -> Self:
        from wealthlab.retirement.social_validation import validate

        validate(self)
        return self
