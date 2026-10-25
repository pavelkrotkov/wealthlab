"""Read-only snapshots retain the authoritative execution order of closed returns.

A consumer may reconcile foreign assessments against actual domestic tax paid.
It receives copies after monthly settlement and again after terminal wash/product
reconciliation. Observing tax positions never pays cash or recalculates a return.
"""

from copy import deepcopy
from datetime import date, timedelta


def observe(observer, ledger, row, phase):
    if observer is None or ledger is None:
        return
    observer(
        dict(
            date=(date.fromisoformat(row["period_end"]) - timedelta(days=1)).isoformat(),
            phase=phase,
            closed_returns=deepcopy(ledger.closed_returns),
            provisional_returns=set(ledger.provisional_returns),
            foreign_payments=deepcopy(ledger.foreign.payments) if ledger.foreign else [],
            foreign_recognized_native=(
                dict(ledger.foreign.recognized_native) if ledger.foreign else {}
            ),
        )
    )
