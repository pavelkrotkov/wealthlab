"""January revisions adjust original-year positions without fabricating tax cash.

Closed cases keep their original payment inputs. The position book separately
tracks cash subsequently paid/received. A corrected liability changes only
outstanding tax and the remaining refund queue. Newly known refunds cannot
arrive before their information date, even under an early refund assumption.
"""

from dataclasses import replace
from datetime import date
from decimal import Decimal

from wealthlab.tax import state_deduction
from wealthlab.tax.annual import evaluate
from wealthlab.tax.facts import FederalIncome

ZERO = Decimal(0)


def revise(ledger, year, amended, when):
    validate_revision(year, amended, when)
    original = ledger.closed_returns[year]
    updated = replace(
        original, case=amended, result=evaluate(amended), net_paid=dict(original.net_paid)
    )
    old_owed, old_refund = original.positions()
    new_owed, new_refund = updated.positions()
    queued = refund(ledger, updated, new_refund, when)
    current, correction = current_case(ledger.case, updated, when, ledger.plan)
    outstanding = revised_outstanding(ledger.outstanding, old_owed, new_owed)
    ledger.closed_returns[year] = updated
    ledger.case = current
    if current.policy.year == year:
        ledger.result = updated.result
    ledger.outstanding = outstanding
    ledger.refunds = [r for r in ledger.refunds if r.get("source_year") != year]
    if queued["cash"]:
        ledger.refunds.append(queued)
    if year == max(ledger.closed_returns):
        ledger.previous = updated.result
    return dict(
        year=year,
        observed=when.isoformat(),
        old_result=original.result,
        final_result=updated.result,
        actual_net_paid=dict(updated.net_paid),
        old_owed=old_owed,
        new_owed=new_owed,
        old_receivable=old_refund,
        new_receivable=new_refund,
        state_refund_income_correction=correction,
        refund_scheduled=queued,
    )


def refund(ledger, position, components, when):
    taxable, treatment = state_deduction.recovery(
        position.case,
        position.result,
        components["new_jersey"],
        ledger.plan.state_refund_taxable_fractions,
    )
    scheduled = date(when.year, ledger.plan.refund_month, 1)
    if scheduled <= when:
        scheduled = date(when.year + when.month // 12, when.month % 12 + 1, 1)
    return dict(
        date=scheduled,
        source_year=position.case.policy.year,
        components=components,
        cash=sum(components.values(), ZERO),
        taxable=taxable,
        treatment=treatment,
    )


def current_case(current, position, when, plan):
    prior_year = position.case.policy.year
    taxable, _ = state_deduction.recovery(
        position.case,
        position.result,
        position.received_state_refund,
        plan.state_refund_taxable_fractions,
    )
    correction = taxable - position.taxable_state_received
    if current.policy.year == prior_year:
        if correction:
            raise ValueError(
                "A terminal reconciliation cannot change already received refund income."
            )
        return position.case, ZERO
    if current.policy.year != when.year:
        raise ValueError("January income corrections need the corresponding current tax year.")
    fed = current.federal_income.model_dump()
    fed.update(
        short_carry=position.result["federal"]["short_carry"],
        long_carry=position.result["federal"]["long_carry"],
        taxable_state_refund=fed["taxable_state_refund"] + correction,
    )
    position.taxable_state_received = taxable
    return current.model_copy(
        update=dict(federal_income=FederalIncome.model_validate(fed))
    ), correction


def revised_outstanding(current, old, new):
    result = {j: current[j] + new[j] - old[j] for j in old}
    if any(value < 0 for value in result.values()):
        raise ValueError("Closed-return payments and outstanding tax do not reconcile.")
    return result


def validate_revision(year, amended, when):
    if when.year != year + 1 or when.month != 1 or amended.policy.year != year:
        raise ValueError(
            "This return-reconciliation profile preserves the year and observes January."
        )
