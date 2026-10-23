"""Sell only explicitly permitted taxable accounts, preserving separate remaining bases."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.tax.funding import solve
from wealthlab.tax.funding_tax import due, proposal


class AccountFunding:
    """Explicit source order controls sales; cash and basis change only after solving.

    This interim adapter realizes a proportional slice of one account's entered
    basis. It does not select tax lots, assume borrowing or infer product liquidity.
    Source character and allowed/denied losses are explicit scenario assumptions.
    """

    def __init__(self, plan, scenario):
        self.sources = plan.funding_sources
        validate_sources(self.sources, scenario)
        self.basis = {item.account_id: (item.federal_basis, item.nj_basis) for item in self.sources}

    def fund(self, ledger, wallet, spending, amounts, start, end) -> Decimal:
        total = Decimal(0)
        for source in self.sources:
            value = wallet.balances[source.account_id]
            if value == 0 or source.liquid_after >= end:
                continue

            def balance(sold, source=source, value=value):
                case = proposal(ledger.case, source, self.basis[source.account_id], value, sold)
                return due(case, ledger, amounts, start, end)

            funding = solve(wallet.cash, spending, value, balance)
            if not funding["converged"]:
                raise ValueError("Tax funding did not converge; no borrowing is assumed.")
            sold = funding["withdrawal"]
            ledger.case = proposal(ledger.case, source, self.basis[source.account_id], value, sold)
            before = self.basis[source.account_id]
            fraction = 1 - sold / value
            self.basis[source.account_id] = (
                money(before[0] * fraction),
                money(before[1] * fraction),
            )
            wallet.balances[source.account_id] -= sold
            wallet.deposit(sold)
            total += sold
            if funding["spending_shortfall"] == 0 and funding["tax_unpaid"] == 0:
                break
        return total


def validate_sources(sources, scenario) -> None:
    accounts = {item.id: item for item in scenario.accounts}
    ids = [item.account_id for item in sources]
    if len(ids) != len(set(ids)):
        raise ValueError("A funding account may appear only once.")
    for source in sources:
        if source.account_id not in accounts or accounts[source.account_id].wrapper != "taxable":
            raise ValueError("Funding sales require an explicitly permitted taxable account.")
