"""One annual comparison with independently auditable mainland and PR inputs."""

from decimal import Decimal
from typing import Literal

from pydantic import Field

from wealthlab.household.records import Money
from wealthlab.tax.annual import AnnualCase
from wealthlab.tax.facts import TaxModel
from wealthlab.tax.pr_residence_facts import Claim, Residence
from wealthlab.tax.pr_source_facts import SourceIncome


class PRCase(TaxModel):
    baseline: AnnualCase
    primary: Residence = Field(default_factory=Residence)
    spouse: Residence = Field(default_factory=Residence)
    income: list[SourceIncome]
    pr_regime: Literal["published_2025", "freeze_2025"] = "published_2025"
    pr_wages_reported_on_form_499r2: Claim = "unset"
    pr_abt_allowed_deductions: Money = Decimal(0)
    pr_allowed_deductions: Money = Decimal(0)
    pr_income_tax_paid_for_us_credit: Money = Decimal(0)
    credit_evidence: str = ""
    description: str = "Original synthetic annual case"
