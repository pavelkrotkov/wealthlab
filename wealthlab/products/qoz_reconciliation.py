"""A timely later-year call amends source-year recognition, never historical cash.

The existing closed-return position book retains actual prior payments/refunds.
Only the outstanding liability or remaining refund queue changes. Existing IRA
fixed elections, future Medicare lookbacks and education income audits consume
the corrected annual result through their already tested reconciliation hooks.
"""

from datetime import date

from wealthlab.portfolio.household_wash_consumers import (
    check_ira,
    medicare_revision,
    update_education,
)
from wealthlab.products.qoz_tax import event
from wealthlab.tax import recognition
from wealthlab.tax.annual import evaluate
from wealthlab.tax.return_reconciliation import apply_revision


def route_exclusion(state, sold, call, exclusion, call_audit):
    if sold.year == call.date.year:
        return exclusion
    amounts = (
        exclusion.federal.long_term,
        exclusion.federal.short_term,
        exclusion.new_jersey.dispositions,
    )
    if not any(amounts):
        return event(call.date, "No eligible prior-year QOZ exclusion")
    validate(state, sold, call)
    taxes = state.tax_ledger
    original = taxes.closed_returns[sold.year].case
    original_event = exclusion.model_copy(update=dict(date=date(sold.year, 12, 31)))
    annual = recognition.event(original, original_event, taxes.plan.state_deduction_mode)
    result = evaluate(annual)
    consumers = prepare_consumers(state.lots, sold.year, annual, result, call.date)
    audit = apply_revision(taxes, sold.year, annual, call.date)
    commit_consumers(state.lots, sold.year, result, consumers)
    audit.update(
        call_id=call.id,
        source_trade_id=call.source_trade_id,
        source_lot_id=call.source_lot_id,
        reason="actual_qoz_reinvestment",
        election=original_event.model_dump(mode="json"),
        ira_eligibility=consumers[0],
    )
    state.revisions.append(audit)
    call_audit["source_return_revision"] = audit
    return event(call.date, "QOZ exclusion belongs to revised source year, not current-year income")


def validate(state, sold, call):
    if not state.plan.prior_source_year_revision_assumed_confirmed:
        raise ValueError("Confirm QOZ prior-source-year return revision assumptions.")
    if call.date.year != sold.year + 1 or not 1 <= call.date.month <= 6:
        raise ValueError(
            "QOZ prior-return revisions only observe the following January through June."
        )
    if sold.year not in state.tax_ledger.closed_returns:
        raise ValueError("QOZ needs the actually closed original source-year return.")
    if state.tax_ledger.case.policy.year != call.date.year:
        raise ValueError("QOZ revisions need the matching current tax year.")


def prepare_consumers(lots, year, annual, result, when):
    checked = check_ira(lots.ira, year, annual, result)
    medicare = medicare_revision(lots.medicare, year, result, when)
    return checked, medicare


def commit_consumers(lots, year, result, prepared):
    if prepared[1] is not None:
        lots.medicare.case = prepared[1]
    update_education(lots.education, year, result, reason="qoz_investment_reconciliation")
