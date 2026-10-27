"""One explicitly sourced QOF entity-asset factor, before native investor costs/distributions."""

from pydantic import Field

from wealthlab.household.records import Identifier
from wealthlab.tax.facts import TaxModel


class QOZBinding(TaxModel):
    account_id: Identifier
    factor: Identifier
    return_source_description: str = Field(min_length=1, max_length=300)
    net_entity_tax_pre_investor_cost_confirmed: bool
    replace_dated_asset_returns_confirmed: bool
