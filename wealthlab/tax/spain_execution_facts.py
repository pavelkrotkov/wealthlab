"""Explicit native Spain identities bind to the single existing foreign-tax cash book."""

from typing import Literal

from pydantic import Field

from wealthlab.household.records import Identifier
from wealthlab.tax.facts import TaxModel
from wealthlab.tax.spain_assessment_inputs import SpainAssessmentPlan


class SpainTaxBinding(TaxModel):
    annual_id: Identifier
    tax_type: Literal["irpf", "wealth", "solidarity"]
    foreign_assessment_id: Identifier
    source: str = Field(min_length=1, max_length=500)


class SpanishSourceLink(TaxModel):
    annual_id: Identifier
    spanish_income_id: Identifier
    us_income_id: Identifier
    source: str = Field(min_length=1, max_length=500)


class SpainExecution(TaxModel):
    assessments: SpainAssessmentPlan
    bindings: list[SpainTaxBinding] = Field(min_length=1)
    source_links: list[SpanishSourceLink]
    us_source_and_spanish_recognition_reconciled_confirmed: bool
    source_reconciliation: str = Field(min_length=1, max_length=1000)
    spanish_foreign_credit_treatment: Literal["denied", "unresolved"]
    credit_treatment_source: str = Field(min_length=1, max_length=1000)
