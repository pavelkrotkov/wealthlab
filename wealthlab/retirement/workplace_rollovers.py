"""Debit source assets once; only funded eligible cash enters the actual IRA receipt book.

Cash distributions run first. An unmet current or prior requirement in this
source plan blocks direct rollover, even when the contingent excise is zero.
Blocked optional requests are not retried and create neither cash nor income.
"""

from decimal import Decimal

from wealthlab.retirement.account_liquidity import blocked
from wealthlab.retirement.ira_rollover_inputs import IncomingIRARollover
from wealthlab.retirement.workplace_withdrawals import month as cash_month

ZERO = Decimal(0)


def before_ira(ledger, wallet, ira, start, end):
    if ledger is None or not ledger.plan.cash_withdrawals:
        return
    orders = ledger.plan.cash_withdrawals.direct_rollovers
    if not orders:
        return
    events, summary = cash_month(ledger, wallet, start, end)
    rows = [
        transfer(ledger, wallet, ira, order)
        for order in sorted(orders, key=lambda o: o.date)
        if start <= order.date < end
    ]
    ledger.rollover_log.extend(rows)
    summary.update(
        workplace_rollover_funded=sum((r["funded"] for r in rows), ZERO),
        workplace_rollover_unfilled=sum((r["unfilled"] for r in rows), ZERO),
    )
    ledger.opening_transfers = events, summary


def transfer(ledger, wallet, ira, order):
    locked = blocked(ledger.plan.liquidity_locks, order.source, order.date)
    required = rmd_block(ledger.rmd, order.source, order.date.year)
    funded = ZERO if locked or required else min(order.amount, wallet.balances[order.source])
    if funded:
        owner = ledger.accounts[order.source].owner
        receipt = IncomingIRARollover(
            **order.model_dump(
                exclude={
                    "amount",
                    "eligible_direct_cash_rollover_to_same_owner_ordinary_ira_confirmed",
                }
            ),
            owner=owner,
            amount=funded,
            federal_basis_transferred=0,
            nj_basis_transferred=0,
            profile="ordinary_qualified_plan_cash_to_same_owner_traditional_ira",
            eligible_direct_rollover_and_rmd_excluded_confirmed=True,
            independent_basis_and_no_special_features_confirmed=True,
            excluded_from_opening_balances_and_cash_receipts_confirmed=True,
        )
        wallet.balances[order.source] -= funded
        ira.rollovers.append(receipt)
    return dict(
        id=order.id,
        date=order.date.isoformat(),
        source=order.source,
        destination=order.destination,
        requested=order.amount,
        funded=funded,
        unfilled=order.amount - funded,
        blocked_by_liquidity=locked,
        source_rmd_unresolved=required,
    )


def rmd_block(book, source, year):
    if book is None:
        return ZERO
    gid = book.source_group[source]
    prior = sum(
        (r["shortfall"] or ZERO for r in book.audit if r["year"] < year and r["plan"] == gid),
        ZERO,
    )
    return book.remaining(gid) + prior
