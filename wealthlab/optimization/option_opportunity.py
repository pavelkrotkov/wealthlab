"""One fixed new option unit has bounded quantities and explicit ownership.

Native execution supports one option book per household. This menu changes only
its integer quantity; the supplied contract, quotes, eligibility and per-unit
fees are shared facts. Zero units create no position or destination account.
"""

from typing import Annotated, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Identifier, Record
from wealthlab.markets.option_inputs import OptionBinding
from wealthlab.products.option_household_inputs import OptionPlan

OptionUnits = Annotated[int, Field(strict=True, ge=0, le=100000)]


class OptionOpportunity(Record):
    cash_account: Identifier
    owner: Identifier
    unit: OptionPlan
    binding: OptionBinding
    minimum_units: OptionUnits = 0
    maximum_units: OptionUnits = 10
    opening_cash_purchase_assumed_confirmed: bool = False
    per_unit_absolute_fees_confirmed: bool = False

    @model_validator(mode="after")
    def bounds(self) -> Self:
        if self.minimum_units > self.maximum_units:
            raise ValueError("Minimum option units cannot exceed maximum units.")
        return self
