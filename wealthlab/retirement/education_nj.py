"""Keep NJBEST deductions and previously deducted principal distinct from earnings.

NJ gross income is supplied for one return, including all modeled items. The
recapture input is a conditional amount from the contribution history; the
engine does not invent a FIFO/proportional convention where none is validated.
"""

from decimal import Decimal


def deduction(income, funded):
    if income is None:
        return None
    return min(Decimal(10000), funded) if income <= 200000 else Decimal(0)


def recapture_income(book, identity, allocation, nonqualified_basis, taxable, fully_qualified):
    recapture = allocation.nj_recaptured_contributions if allocation else None
    if recapture is not None and recapture > nonqualified_basis:
        raise ValueError("NJ recapture cannot exceed the returned nonqualified principal.")
    account = book["accounts"][identity]
    if not book["plans"][account.plan].njbest:
        if recapture:
            raise ValueError("NJBEST deduction recapture cannot be assigned to another plan.")
        recapture = Decimal(0)
    if fully_qualified:
        recapture = Decimal(0)
    return dict(
        nj_taxable_earnings=taxable,
        nj_recaptured_contributions=recapture,
        nj_total_income=None if recapture is None else taxable + recapture,
    )
