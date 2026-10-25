"""A dated supplied grant/compliance claim; application never implies a decree."""

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import Field

from wealthlab.household.records import Money
from wealthlab.tax.facts import TaxModel
from wealthlab.tax.pr_facts import PRCase
from wealthlab.tax.pr_residence_facts import Claim


class Decree(TaxModel):
    # A supplied eligibility-history claim must cover the old residence window
    # and, for post-2026 applications, the new six-year nonresidence condition.
    # The app does not adjudicate those legal facts or create a grant.

    status: Literal["unset", "assumed", "confirmed", "denied"] = "unset"
    application_date: date | None = None
    granted_on: date | None = None
    effective_from: date | None = None
    valid_until: date | None = None
    residence_since: date | None = None
    prior_residence_window_2006_2012: Claim = "unset"
    six_prior_years_nonresident: Claim = "unset"
    eligibility_history: Claim = "unset"
    compliance: Claim = "unset"
    not_revoked: Claim = "unset"
    legacy_transition_election: bool = False
    annual_compliance_cost: Money | None = None
    evidence: str = ""


class MarketableGain(TaxModel):
    income_index: int = Field(ge=0)
    acquired: date
    sale_proceeds: Money
    federal_cost: Money
    pr_cost: Money
    federal_possession_start: date
    federal_move_fmv: Money
    pr_move_fmv: Money
    pr_resident_since: date
    ordinary_public_stock_classification: Claim = "unset"
    actively_traded_throughout: Claim = "unset"
    continuous_residence: Claim = "unset"
    us_non_bfr_in_prior_ten_years: Literal["yes", "no", "unset"] = "unset"
    federal_fmv_election: Claim = "unset"
    evidence: str = ""


class PRComparison(TaxModel):
    annual: PRCase
    decree: Decree = Field(default_factory=Decree)
    gains: list[MarketableGain] = Field(default_factory=list)
    description: str = "Original synthetic conditional decree comparison"
    other_preferential_entitlement: Claim = "unset"
    prior_abt_credit: Money = Decimal(0)
