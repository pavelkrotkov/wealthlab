"""Supplied owned wealth, prelimited credits and observed tax settlements."""

from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Money
from wealthlab.tax.facts import TaxModel
from wealthlab.tax.spain_money import SpanishAmount

Source = Annotated[str, Field(min_length=1, max_length=500)]
Share = Annotated[Decimal, Field(gt=0, le=1)]
Product = Literal["ordinary", "us_retirement", "us_insurance", "us_partnership"]


class SpanishAsset(TaxModel):
    """Value the whole asset, then apply ownership and the supplied per-person exemption."""

    id: Identifier
    owner_id: Identifier
    ownership_share: Share
    product: Product
    kind: Literal["financial", "property", "insurance", "business", "other"]
    fiscal_value: SpanishAmount
    fiscal_valuation_source: Source
    treatment: Literal["included", "principal_home", "supplied_exemption", "unknown"]
    exemption_eur: Money
    classification_source: Source
    nonproductive: bool | None


class SpanishDebt(TaxModel):
    """The deductible amount is already limited to this person and the nonexempt asset portion."""

    id: Identifier
    owner_id: Identifier
    ownership_share: Share
    balance: SpanishAmount
    deductible_eur: Money
    related_asset_id: Identifier | None
    eligibility_source: Source


class SpanishCredits(TaxModel):
    """Independently prelimited entitlements; these never create a cash receipt."""

    irpf_state: Money
    irpf_regional: Money
    wealth_foreign: Money
    wealth_regional: Money
    solidarity_foreign: Money
    source: Source
