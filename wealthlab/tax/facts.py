"""Annual recognized amounts; eligibility and allowed deductions are explicit inputs."""

from decimal import Decimal
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from wealthlab.household.records import Money

SignedMoney = Annotated[Decimal, Field(max_digits=18, decimal_places=2)]


class TaxModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)


class FederalIncome(TaxModel):
    wages_primary: Money = Decimal(0)
    wages_spouse: Money = Decimal(0)
    deferrals_primary: Money = Decimal(0)
    deferrals_spouse: Money = Decimal(0)
    taxable_state_refund: Money = Decimal(0)
    interest: Money = Decimal(0)
    tax_exempt_interest: Money = Decimal(0)
    dividends: Money = Decimal(0)
    qualified_dividends: Money = Decimal(0)
    ira_distributions: Money = Decimal(0)
    taxable_pension: Money = Decimal(0)
    social_security: Money = Decimal(0)
    allowed_passive_income: SignedMoney = Decimal(0)
    short_term: SignedMoney = Decimal(0)
    long_term: SignedMoney = Decimal(0)
    collectibles_component: SignedMoney = Decimal(0)
    short_carry: Money = Decimal(0)
    long_carry: Money = Decimal(0)

    @model_validator(mode="after")
    def validate_components(self) -> Self:
        if self.qualified_dividends > self.dividends:
            raise ValueError("Qualified dividends are included in total dividends.")
        return self


class Deductions(TaxModel):
    medical: Money = Decimal(0)
    state_local_income_tax_paid: Money = Decimal(0)
    property_tax_paid: Money = Decimal(0)
    qualified_mortgage_interest: Money = Decimal(0)
    cash_charity: Money = Decimal(0)
    noncash_charity: Money = Decimal(0)
    eligible_care_expenses: Money = Decimal(0)
