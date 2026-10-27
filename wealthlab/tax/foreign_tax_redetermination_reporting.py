"""Export final native source-return positions after every terminal reconciliation.

Revision histories record what became known and owed at each observation.
The final source map instead reads authoritative closed returns after actual
arrears/refunds and later wash/product reconciliation. No history sorting or
second tax calculation is needed to select a return's executed final state.
"""


def finish(ledger, rows):
    if ledger is None or ledger.foreign is None:
        return
    result = {}
    for year in sorted(ledger.foreign.revised_years):
        position = ledger.closed_returns[year]
        owed, receivable = position.positions()
        result[year] = dict(
            final_result=position.result,
            actual_net_paid=dict(position.net_paid),
            owed=owed,
            receivable=receivable,
            provisional=year in ledger.provisional_returns,
        )
    rows[-1]["foreign_final_source_returns"] = result
