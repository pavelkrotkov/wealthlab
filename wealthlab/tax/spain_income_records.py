"""Native tagged records prevent net dollar gains from being translated at one closing rate."""

from typing import Annotated, Literal

from pydantic import Field

from wealthlab.household.records import Identifier
from wealthlab.tax.facts import TaxModel
from wealthlab.tax.spain_money import SpanishAmount
from wealthlab.tax.spain_records import Product, Source


class IncomeFacts(TaxModel):
    id: Identifier
    owner_id: Identifier
    source_country: str = Field(min_length=2, max_length=2)
    product: Product
    spanish_base: Literal["general", "savings", "exempt", "exempt_with_progression", "unknown"]
    treatment: Literal["allowed", "deferred", "denied", "unknown"]
    classification_source: Source
    treaty_treatment: Literal["none", "supplied_exemption", "supplied_credit", "unknown"]
    treaty_source: Source


class SpanishOrdinaryIncome(IncomeFacts):
    kind: Literal["income"]
    amount: SpanishAmount

    def euros(self):
        return self.amount.euros()


class SpanishDisposal(IncomeFacts):
    kind: Literal["disposal"]
    proceeds: SpanishAmount
    acquisition: SpanishAmount

    def euros(self):
        return self.proceeds.euros() - self.acquisition.euros()


SpanishIncome = Annotated[SpanishOrdinaryIncome | SpanishDisposal, Field(discriminator="kind")]
