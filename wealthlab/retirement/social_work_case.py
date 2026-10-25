"""The ordinary claim case supplies a no-work counterfactual, not a no-work factual assertion."""

from typing import Self

from pydantic import model_validator

from wealthlab.retirement.social_inputs import SocialCase
from wealthlab.retirement.social_work_inputs import WorkPolicy
from wealthlab.tax.facts import TaxModel


class SocialWorkCase(TaxModel):
    claims: SocialCase
    work: WorkPolicy

    @model_validator(mode="after")
    def valid(self) -> Self:
        from wealthlab.retirement.social_work_validation import validate

        validate(self)
        return self
