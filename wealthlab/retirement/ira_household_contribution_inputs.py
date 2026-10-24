"""Annual IRA eligibility forecasts have no separate household cash or asset book."""

from typing import Literal

from pydantic import Field

from wealthlab.retirement.contribution_assumptions import RuleMode
from wealthlab.retirement.contribution_inputs import ContributionOrder, Contributor
from wealthlab.tax.facts import TaxModel


class IRAContributionYear(TaxModel):
    year: int = Field(ge=2025, le=2200)
    rule_mode: RuleMode = "published"
    filing: Literal["single", "joint", "separate", "head", "surviving"]
    lived_with_spouse: bool
    spouse_covered_by_workplace_plan: bool
    contributors: list[Contributor] = Field(min_length=1, max_length=2)


class IRAHouseholdContributions(TaxModel):
    years: list[IRAContributionYear] = Field(min_length=1)
    orders: list[ContributionOrder]
    complete_annual_elections_and_context_confirmed: bool
    timing: Literal["month_end_after_receipts_before_current_tax_and_spending"]
