"""Cash-basis NJ deductions and explicitly conditional refund recoveries."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.tax.annual import evaluate


def nj_paid(case) -> Decimal:
    return case.payments.nj_withheld + case.payments.nj_estimates


def add(case, amount: Decimal, mode: str):
    if mode == "entered" or amount == 0:
        return case
    deductions = case.federal_deductions
    updated = deductions.model_copy(
        update={"state_local_income_tax_paid": deductions.state_local_income_tax_paid + amount}
    )
    return case.model_copy(update={"federal_deductions": updated})


def recovery(case, result, refund: Decimal, fractions: dict) -> tuple[Decimal, str]:
    """Never infer a positive taxable recovery from the refund alone.

    No federal deduction/tax benefit means zero recovery. A benefit otherwise
    requires an explicit scenario fraction established from the prior return's
    Pub. 525 worksheet, including sales-tax alternative, AMT and credits.
    """
    if refund == 0:
        return Decimal(0), "No state refund"
    year = case.policy.year
    if year in fractions:
        return money(refund * fractions[year]), "Explicit taxable-fraction assumption"
    federal = result["federal"]
    if federal["itemized_deduction"] == 0:
        return Decimal(0), "Standard deduction: no recovered itemized deduction"
    paid = case.federal_deductions.state_local_income_tax_paid
    counterfactual = add(case, -min(paid, refund), "actual_payments")
    other = evaluate(counterfactual)["federal"]
    unchanged = all(
        other[key] == federal[key] for key in ("income_tax", "short_carry", "long_carry")
    )
    if unchanged:
        return Decimal(0), "Recomputed prior federal tax unchanged"
    raise ValueError(
        f"NJ refund for {year} may recover a federal deduction. Set "
        f"state_refund_taxable_fractions[{year}] to an explicit 0-1 assumption "
        "from the prior-year tax-benefit worksheet; no tax-free refund is inferred."
    )
