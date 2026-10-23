"""Tax filing unit and explicit dependent eligibility, without personal identifiers."""

from typing import Literal, Self

from pydantic import Field, model_validator

from wealthlab.tax.facts import TaxModel


class Dependent(TaxModel):
    age: int = Field(ge=0, le=120)
    child_credit_eligible: bool
    earned_income_credit_eligible: bool
    care_credit_eligible: bool


class Filing(TaxModel):
    status: Literal["single", "joint", "separate", "head", "surviving"]
    age_primary: int = Field(ge=18, le=120)
    age_spouse: int = Field(ge=0, le=120)
    dependents: list[Dependent]

    @model_validator(mode="after")
    def validate_ages(self) -> Self:
        if self.status == "joint" and self.age_spouse < 18:
            raise ValueError("Joint filing requires an adult spouse age.")
        if any(item.child_credit_eligible and item.age >= 17 for item in self.dependents):
            raise ValueError("A child tax credit dependent must be younger than 17.")
        return self
