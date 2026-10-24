"""NJ nonqualified Roth earnings follow the IRA worksheet, independently of federal."""

from wealthlab.retirement.ira_reconciliation import recovered, value


def reconcile(book, person, rows, converted):
    # Converted principal includes already-taxed traditional basis plus earnings
    # recognized on conversion, so the full converted amount enters NJ Roth basis.
    states = {row["roth_qualified"] for row in rows if row["paid"]}
    if len(states) > 1:
        raise ValueError(
            "Mixed qualified/nonqualified Roth withdrawals in one year need a validated NJ "
            "allocation model; this annual IRA layer cannot calculate that case yet."
        )
    basis = person.nj_roth_basis + converted
    remaining = recovered(rows, basis, value(book, person.id, "roth"), "nj_basis_recovered")
    for row in rows:
        row["nj_taxable"] = 0 if row["roth_qualified"] else row["paid"] - row["nj_basis_recovered"]
    return remaining
