"""Explicit full-account factor proxies; they do not disclose underlying issuer holdings."""

from typing import Literal

from wealthlab.household.records import Identifier
from wealthlab.tax.facts import TaxModel


class WrapperBinding(TaxModel):
    account_id: Identifier
    factor: Identifier
    return_convention: Literal["mark_plus_yield_on_month_end_balance"]
    liquidity_convention: Literal["block_outgoing_withdrawals_and_conversions"]
    replace_entered_returns_confirmed: bool
