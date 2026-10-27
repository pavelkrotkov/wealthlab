"""Keep contingent value, redemption rights and concentration separate from household cash.

The concentration denominator is gross marked assets plus contingent unvested
value. It does not convert a locked balance into a spendable resource, and it
is not a ratio to after-tax exit wealth.
"""

from datetime import timedelta
from decimal import Decimal

from wealthlab.employment.compensation_exit_state import evidence
from wealthlab.retirement.account_liquidity import blocked


def snapshot(ledger, wallet, end):
    unvested = sum((s["unvested"] for s in ledger.states.values()), Decimal(0))
    vested = sum((s["vested"] for s in ledger.states.values()), Decimal(0))
    redeemable = sum(
        (
            ledger.states[t.id]["vested"]
            for t in ledger.plan.tranches
            if t.liquid_from < end
            and not blocked(ledger.plan.liquidity_locks, t.account, end - timedelta(days=1))
        ),
        Decimal(0),
    )
    exposure = vested + unvested
    assets = sum(wallet.balances.values()) + unvested
    return dict(
        employer_unvested_contingent=unvested,
        employer_vested=vested,
        employer_locked_vested=vested - redeemable,
        employer_redeemable=redeemable,
        employer_distribution_requested=ledger.requested,
        employer_distribution_cash=ledger.distributed,
        employer_distribution_not_paid=ledger.requested - ledger.distributed,
        employer_exposure=exposure,
        employer_share_of_assets_plus_contingent=exposure / assets if assets else Decimal(0),
        employer_tranches=[tranche_snapshot(ledger, wallet, t, end) for t in ledger.plan.tranches],
    )


def tranche_snapshot(ledger, wallet, tranche, end):
    row = dict(tranche=tranche.id, account=tranche.account, **ledger.states[tranche.id])
    # Full forensic lists belong in the terminal audit, not each simulated month.
    if end == ledger.horizon_end:
        row["exit_evidence"] = evidence(ledger, wallet, tranche, end)
    return row
