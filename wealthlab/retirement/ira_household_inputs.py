"""Fixed IRA schedules share household cash; annual pools retain their own history."""

from typing import Literal

from pydantic import Field

from wealthlab.retirement.distribution_inputs import (
    AccountReturn,
    DistributionOwner,
    WithdrawalOrder,
)
from wealthlab.tax.facts import TaxModel


class IRAPlan(TaxModel):
    owners: list[DistributionOwner] = Field(min_length=1, max_length=2)
    products: dict[str, Literal["traditional_ira", "roth_ira"]]
    orders: list[WithdrawalOrder]
    returns: list[AccountReturn]
    complete_ordinary_ira_pools_confirmed: bool
    other_tax_inputs_exclude_ira_events_confirmed: bool
    reconciliation: Literal["year_end_fixed_schedule"]
