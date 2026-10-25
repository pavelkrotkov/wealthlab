"""The supplied full-cash liquidation executes only when all modeled claims can settle.

A failed request leaves the property unsold, preserving production and creditor
exposure. Partial property sales need independently supplied inside-basis and
dated tax-recognition facts, outside this debt-free full-liquidation adapter.
"""

from wealthlab.products.drilling_cash import ZERO


def funded(ledger, observation):
    resources = ledger.cash + observation.exit_gross_proceeds
    claims = sum(ledger.owed.values(), ZERO) + observation.exit_fee
    return not ledger.call_owed and resources >= claims
