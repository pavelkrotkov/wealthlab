"""HSA transfers and direct provider distributions have separate cash destinations.

All actual distributions still enter qualified/nonqualified tax totals. A
provider payment must not also appear as a household cash receipt; the bill
book reports that spending and any unpaid liability in the healthcare slot.
"""

from decimal import Decimal

from wealthlab.retirement.contribution_assumptions import rule_year
from wealthlab.retirement.hsa_household_tax import totals

ZERO = Decimal(0)


def summary(rows, amounts):
    withdrawals = [r for r in rows if r["kind"] == "withdrawal"]
    return dict(
        hsa_personal_contributions=amounts["personal"],
        hsa_employer_funding=amounts["employer"],
        hsa_bank_interest=amounts["interest"],
        hsa_qualified_reimbursements=amounts["qualified"],
        hsa_nonqualified_taxable=amounts["federal_taxable"],
        hsa_additional_tax=amounts["federal_additional_tax"],
        hsa_nj_withdrawal_income=amounts["nj_taxable"],
        hsa_withdrawal_cash=sum(
            (r["funded"] for r in withdrawals if r.get("cash_destination") != "medical_provider"),
            ZERO,
        ),
        hsa_unfilled_requests=sum(
            (
                r.get("unfilled", r.get("unfunded", ZERO)) + r.get("blocked_by_limit", ZERO)
                for r in rows
            ),
            ZERO,
        ),
    )


def annual(ledger):
    return dict(
        **totals(ledger.book["rows"]),
        year=ledger.year,
        rule_mode=ledger.context.rule_mode,
        rule_base_year=rule_year(ledger.context),
        contribution_limits=dict(ledger.book["limits"]),
        personal_federal_deduction=ledger.book["personal"],
        employer_funding=ledger.book["employer"],
        bank_interest=ledger.book["interest"],
        nj_treatment=ledger.plan.nj_treatment,
        remaining_receipts=dict(ledger.book["receipt_remaining"]),
    )
