"""Explicit qualified-plan identity, beneficiary table and conditional excise policy."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field, model_validator

from wealthlab.household.records import Identifier
from wealthlab.tax.facts import TaxModel

Rate = Annotated[Decimal, Field(ge=0, le=1, max_digits=12, decimal_places=10)]


class RMDGroup(TaxModel):
    sources: list[Identifier] = Field(min_length=1)
    complete_distinct_plan_balances_and_distributions_confirmed: bool
    beneficiary_table_eligibility_confirmed: bool
    rmd_table: Literal["uniform", "sole_younger_spouse"]
    spouse_birth_date: date | None = None


class WorkplaceRMDPlan(TaxModel):
    groups: dict[Identifier, RMDGroup] = Field(min_length=1)
    rule_mode: Literal["frozen_2026_rmd_rules_assumption"]
    deadline: Literal["december_target_no_first_year_deferral"]
    automatic_december_catchup: bool
    no_unmodeled_opening_shortfalls_confirmed: bool
    noneligible_federal_withholding_rate: Rate = Decimal(".10")
    automatic_nj_withholding_rate: Rate = Decimal(0)
    shortfall_treatment: Literal[
        "ordinary_25_percent",
        "timely_correction_10_percent_assumption",
        "irs_waiver_allowed_assumption",
    ] = "ordinary_25_percent"
    conditional_relief_confirmed: bool = False

    @model_validator(mode="after")
    def policy(self):
        if self.noneligible_federal_withholding_rate + self.automatic_nj_withholding_rate > 1:
            raise ValueError("RMD source withholding cannot exceed gross cash.")
        if (
            self.shortfall_treatment != "ordinary_25_percent"
            and not self.conditional_relief_confirmed
        ):
            raise ValueError(
                "Confirm conditional correction/IRS waiver assumptions for RMD excise relief."
            )
        return self
