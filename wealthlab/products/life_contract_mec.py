"""Income-first MEC receipts and the special taxed-loan basis rule of72(e)(4).

A loan is a deemed receipt for income, but not ordinary basis recovery. Only its
included income increases investment. Repayment does not add another premium.
Capitalized interest is a new deemed loan only under an explicitly supplied term.
"""

from decimal import Decimal

from wealthlab.products.life_contract_tax import LOANS

ZERO = Decimal(0)


def recognize(contract, event, basis):
    if event.cash_value_before is None:
        return None, None
    if event.kind not in LOANS and event.amount > event.cash_value_before:
        raise ValueError("MEC cash receipt exceeds supplied pre-receipt policy value.")
    taxable = min(event.amount, max(ZERO, event.cash_value_before - basis))
    if event.kind not in LOANS:
        return taxable, basis - (event.amount - taxable)
    if (
        event.kind == "capitalized_interest"
        and not contract.capitalized_interest_is_new_loan_confirmed
    ):
        return None, None
    return taxable, basis + taxable
