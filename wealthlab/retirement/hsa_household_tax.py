"""Actual cash-HSA recognition with explicit noninvestment and independent NJ assumptions.

The funded withdrawal, never the requested amount, creates taxable ingredients.
NJ fractions apply to the entire funded withdrawal, independently of federal
receipt matching. This does not infer historical NJ basis or investment tax.
"""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import TaxEvent

ZERO = Decimal(0)


def validate(plan):
    ids = {w.id for w in plan.withdrawals}
    nonqualified = {w.id for w in plan.withdrawals if w.mode == "allow_nonqualified"}
    if set(plan.nj_withdrawal_taxable_fractions) - ids:
        raise ValueError("NJ HSA withdrawal fractions must reference known withdrawal IDs.")
    validate_treatment(plan, nonqualified)
    if not nonqualified.issubset(plan.nj_withdrawal_taxable_fractions):
        raise ValueError(
            "Supply an independent NJ taxable fraction for each nonqualified HSA order."
        )


def validate_treatment(plan, nonqualified):
    if nonqualified and plan.nonqualified_treatment != "ordinary_noninvestment_assumption":
        raise ValueError(
            "Nonqualified household HSA withdrawals require an explicit tax assumption."
        )
    if (nonqualified or plan.nj_withdrawal_taxable_fractions) and not (
        plan.generated_distribution_tax_excluded_from_other_inputs_confirmed
    ):
        raise ValueError(
            "Confirm generated HSA distribution taxes are excluded from other tax inputs."
        )


def annotate(rows, plan):
    for row in rows:
        if row["kind"] == "withdrawal":
            fraction = plan.nj_withdrawal_taxable_fractions.get(row["id"], ZERO)
            row["nj_taxable"] = money(row["funded"] * fraction)


def totals(rows):
    withdrawals = [r for r in rows if r["kind"] == "withdrawal"]
    fields = ("qualified", "federal_taxable", "federal_additional_tax", "nj_taxable")
    return {key: sum((r[key] for r in withdrawals), ZERO) for key in fields}


def event(when, amounts):
    return TaxEvent(
        date=when,
        description="Actual cash-HSA contributions, distributions and conditional NJ recognition",
        cash_received=0,
        federal=FederalIncome(
            deductible_hsa_contributions=amounts["personal"],
            ordinary_noninvestment_income=amounts["federal_taxable"],
            retirement_additional_tax=amounts["federal_additional_tax"],
        ),
        new_jersey=NJIncome(
            wages=amounts["employer"], interest=amounts["interest"], other=amounts["nj_taxable"]
        ),
    )
