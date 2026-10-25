"""Release only unreserved actual cash; collateral and noncash option marks cannot pay bills."""

from decimal import Decimal

from wealthlab.products.household_cash import transfer
from wealthlab.products.option_reporting import snapshot


def settle(ledger, wallet, before, mark):
    state = ledger.state
    transfer(wallet, state.reserve - before)
    state.reserve = Decimal(0)
    row = snapshot(state, mark)
    free = max(Decimal(0), state.book.cash[state.account] - state.collateral)
    state.book.cash[state.account] -= free
    repaid = min(free, state.loan)
    state.loan -= repaid
    free -= repaid
    wallet.deposit(free)
    equity = row["wealth"] - free
    # Principal repayment reduces assets and debt equally; only net released cash leaves equity.
    wallet.balances[ledger.plan.account_id] = max(Decimal(0), equity)
    ledger.summary = dict(
        option_liability=max(Decimal(0), -equity),
        option_loan=state.loan,
        option_margin_unfunded=row["collateral_shortfall"],
        option_cash_released=free,
        option_shares=row["shares"],
        option_collateral=row["collateral"],
        option_federal_basis=row["federal_basis"],
        option_nj_basis=row["nj_basis"],
        option_failed=bool(state.failures),
    )
    ledger.log.append(
        dict(
            row,
            account_id=ledger.plan.account_id,
            released_cash=free,
            failures=list(state.failures),
        )
    )
