"""Read native balances and debt without changing their economic or tax books.

HSA custodian debt stays a household liability; subtracting it here determines
only the named net-equity fee base. Policy loans are already deducted in native
net values. Initial policy values are dated opening inputs, never later marks.
"""

from copy import deepcopy
from decimal import Decimal

ZERO = Decimal(0)


def observed(accounts, when, cutoff, wallet, life, debts):
    """Custody debt reduces only the fee base, preserving native accounts and liabilities."""
    balances = {
        a: max(ZERO, wallet.balances[a] - debts.get(a, ZERO))
        for a in accounts
        if a in wallet.balances
    }
    return deepcopy(
        dict(
            date=when.isoformat(),
            cutoff=cutoff,
            account_net_equity=balances,
            observed_account_fee_debt={a: debts[a] for a in accounts if a in debts},
            life_values=[value for value in life if value["account_id"] in accounts],
            source="Actual native projection state at the named cutoff",
        )
    )


def hsa_debts(hsa):
    investments = getattr(hsa, "investments", None)
    return dict(investments.ledger.book.fee_owed) if investments is not None else {}


def opening_life(scenario):
    if scenario.life_plan is None:
        return []
    return [
        dict(
            account_id=h.account_id,
            net_cash_value=max(ZERO, h.opening_values.gross_cash_value - h.contract.opening_loan),
            net_surrender_value=max(
                ZERO, h.opening_values.gross_surrender_value - h.contract.opening_loan
            ),
            loan=h.contract.opening_loan,
        )
        for h in scenario.life_plan.holdings
    ]
