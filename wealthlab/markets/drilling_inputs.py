"""Explicit price-factor proxies preserve independent fixed drilling contract/tax facts."""

from typing import Annotated

from pydantic import Field

from wealthlab.household.records import Identifier, Money
from wealthlab.tax.facts import TaxModel


class DrillingBinding(TaxModel):
    account_id: Identifier
    commodity_factor: Identifier
    reference_factor: Identifier
    opening_commodity_price: Annotated[Money, Field(gt=0)]
    replace_price_observations_confirmed: bool = False
    fixed_production_cost_tax_and_property_exit_quotes_valid_for_prices_confirmed: bool = False
    validity_source: str = Field(min_length=10, max_length=1000)
