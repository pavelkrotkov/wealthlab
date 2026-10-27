"""Stable person/year assessments and remaining supplied EUR tax obligations."""

from datetime import date
from typing import Literal, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Identifier, Money
from wealthlab.tax.facts import TaxModel
from wealthlab.tax.spain_inputs import SpainCase
from wealthlab.tax.spain_records import Source


class SpanishAnnualAssessment(TaxModel):
    id: Identifier
    case: SpainCase


class SpanishTaxObligation(TaxModel):
    """Remaining schedule as of this plan; the external cash book owns executed allocations."""

    id: Identifier
    assessment_id: Identifier
    tax_type: Literal["irpf", "wealth", "solidarity"]
    due_date: date
    amount_eur: Money
    source: Source


class SpainAssessmentPlan(TaxModel):
    synthetic: bool
    as_of: date
    annuals: list[SpanishAnnualAssessment] = Field(min_length=1)
    obligations: list[SpanishTaxObligation]

    @model_validator(mode="after")
    def coherent(self) -> Self:
        from wealthlab.tax.spain_assessment_validation import validate

        validate(self)
        return self
