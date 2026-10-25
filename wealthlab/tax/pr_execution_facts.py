"""Prepared PR federal context retains worldwide facts and stable source identities.

This optional annual context uses the existing PR residence/source policy.
Amounts remain worldwide in AnnualCase for payroll and independent NJ facts;
only the prepared federal income-tax calculation excludes eligible PR rows.
"""

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Money
from wealthlab.tax.facts import TaxModel
from wealthlab.tax.pr_residence_facts import Claim, Residence
from wealthlab.tax.pr_source_facts import SourceIncome


class PRFederalSource(TaxModel):
    id: Identifier
    owner_id: Identifier
    income: SourceIncome
    classification_assumed_confirmed: bool


class PRFederalProfile(TaxModel):
    as_of: date
    people: dict[Identifier, Literal["primary", "spouse"]] = Field(min_length=1, max_length=2)
    primary: Residence
    spouse: Residence = Field(default_factory=Residence)
    sources: list[PRFederalSource]
    pr_regime: Literal["published_2025", "freeze_2025"]
    pr_wages_reported_on_form_499r2: Claim
    pr_allowed_deductions: Money = Decimal(0)
    pr_abt_allowed_deductions: Money = Decimal(0)
    source: str = Field(min_length=1, max_length=500)
