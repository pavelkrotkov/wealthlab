"""Actual refund observations revise original native returns and carry vintages atomically.

A copied tax-position book validates all affected years before committing any
revision. Native reconciliation preserves actual net tax paid and schedules
only newly known balances/refunds; the real wallet is never copied or paid by
this calculation. The caller pays resulting native arrears through its usual
required-tax priority after the complete revision succeeds.
"""

from copy import copy, deepcopy

from wealthlab.tax.foreign_credit import evaluate
from wealthlab.tax.foreign_credit_facts import ForeignCredits
from wealthlab.tax.foreign_tax_credits import carry_reasons
from wealthlab.tax.foreign_tax_redetermination_facts import original_case, pending
from wealthlab.tax.return_reconciliation import apply_revision

POSITION_FIELDS = ("case", "result", "previous", "outstanding", "refunds", "closed_returns")


def reconcile(book, ledger, when):
    refunds = pending(book, when)
    if not refunds:
        return
    try:
        validate_policy(book)
        trial_book, trial_ledger = prepare(book, ledger)
        revisions = revise_years(trial_book, trial_ledger, min(year for _, year in refunds), when)
    except ValueError as error:
        book.redetermination_unresolved = [str(error)]
        return
    for field in POSITION_FIELDS:
        setattr(ledger, field, getattr(trial_ledger, field))
    book.credit_results = trial_book.credit_results
    identities = [record.id for record, _ in refunds]
    book.redetermined_refunds.update(identities)
    book.revised_years.update(row["year"] for row in revisions)
    book.redetermination_unresolved = []
    book.month_redeterminations.extend(dict(row, actual_refund_ids=identities) for row in revisions)


def validate_policy(book):
    if (
        book.plan.prior_return_redetermination != "allowed"
        or not book.plan.redetermination_source.strip()
    ):
        raise ValueError("Confirm original-return treatment and supporting evidence.")


def prepare(book, ledger):
    trial_book, trial_ledger = copy(book), copy(ledger)
    trial_book.credit_results = dict(book.credit_results)
    trial_ledger.closed_returns = deepcopy(ledger.closed_returns)
    trial_ledger.outstanding = dict(ledger.outstanding)
    trial_ledger.refunds = deepcopy(ledger.refunds)
    return trial_book, trial_ledger


def revise_years(book, ledger, first, when):
    if first not in ledger.closed_returns:
        raise ValueError(
            "The actual original paid-year US return is unavailable for redetermination."
        )
    revisions = []
    for year in range(first, when.year):
        validate_year(book, ledger, year)
        original = ledger.closed_returns[year]
        case = original_case(book, original.case, when)
        result = evaluate(case)
        if result["candidate"] is None:
            raise ValueError(
                "Original-return credit redetermination is blocked: "
                + "; ".join(result["unresolved"])
            )
        amount = result["candidate"]["federal"]["foreign_tax_credit"]
        facts = ForeignCredits(regular=amount, eligibility=case.eligibility, source=case.source)
        amended = original.case.model_copy(update=dict(foreign_credits=facts))
        revisions.append(apply_revision(ledger, year, amended, when))
        book.credit_results[year] = result
    return revisions


def validate_year(book, ledger, year):
    if year in ledger.provisional_returns:
        raise ValueError("Original-return redetermination needs finalized source-year facts.")
    reasons = carry_reasons(book, year)
    if reasons:
        raise ValueError("Original-return carry disposition is unresolved: " + "; ".join(reasons))


def cost_reasons(book):
    if book.revised_years and not book.plan.redetermination_other_costs_complete_confirmed:
        return ["Redetermination interest/penalty/compliance costs need dated expense facts."]
    return []
