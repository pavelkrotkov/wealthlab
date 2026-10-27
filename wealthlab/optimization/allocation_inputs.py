"""Fixed, supplied new-investment unit profiles funded only from existing liquid cash.

Units scale monetary schedules, never rates, dates, eligibility or market
assumptions. Existing positions cannot become an opportunity: the destination
must be new, and the cash purchase is an explicit opening scenario assumption.
"""

from typing import Annotated, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Identifier, Record
from wealthlab.products.household_inputs import HouseholdSleeve

Units = Annotated[int, Field(ge=0, le=1000000)]


class SleeveOpportunity(Record):
    cash_account: Identifier
    owner: Identifier
    unit: HouseholdSleeve
    minimum_units: Units = 0
    maximum_units: Units = 100
    opening_cash_purchase_assumed_confirmed: bool = False
    proportional_dollar_schedules_assumed_confirmed: bool = False
    replace_observations_with_shared_paths_confirmed: bool = False

    @model_validator(mode="after")
    def bounds(self) -> Self:
        if self.minimum_units > self.maximum_units:
            raise ValueError("Minimum purchase units cannot exceed maximum units.")
        return self
