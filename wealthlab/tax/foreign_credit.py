"""Actual paid-tax FX and ordinary basket limits feed the existing federal engine.

Credit is a liability adjustment, never spendable refund cash. The independently
entered mainland NJ return remains visible; no relocation or NJ foreign credit
is inferred. Household funding and jurisdictional residence adapters are separate.
"""

from decimal import Decimal

from wealthlab.tax.annual import evaluate as annual
from wealthlab.tax.foreign_credit_carries import carry_disposition
from wealthlab.tax.foreign_credit_cash import observe
from wealthlab.tax.foreign_credit_facts import ForeignCredits
from wealthlab.tax.foreign_credit_fx import reasons as fx_reasons
from wealthlab.tax.foreign_credit_limits import calculate
from wealthlab.tax.foreign_credit_scope import reasons
from wealthlab.tax.foreign_credit_sources import reconcile
from wealthlab.tax.foreign_credit_validation import validate

ZERO = Decimal(0)


def evaluate(case, *, redetermined_refunds=()):
    validate(case)
    baseline, cash_rows = annual(case.annual), observe(case)
    result = payment_snapshot(case, baseline, cash_rows)
    if case.eligibility == "denied":
        blocked = fx_reasons(case, cash_rows) + revision_reasons(
            case, cash_rows, redetermined_refunds
        )
        return dict(
            result,
            candidate=None if blocked else baseline,
            unresolved=blocked,
            credit_status="denied; no credit or refund cash assumed",
        )
    blocked = (
        reasons(case, baseline)
        + fx_reasons(case, cash_rows)
        + revision_reasons(case, cash_rows, redetermined_refunds)
    )
    if blocked:
        return dict(result, unresolved=blocked, credit_status="blocked")
    reconcile(case)
    audit, used = calculate(case, baseline, cash_rows)
    credit = sum((r["claimed"] for r in audit), ZERO)
    facts = ForeignCredits(regular=credit, eligibility="allowed", source=case.source)
    candidate = annual(case.annual.model_copy(update=dict(foreign_credits=facts)))
    if candidate["federal"]["amt"]:
        return dict(
            result,
            unresolved=["The regular credit requires a separate AMT-credit profile."],
            basket_audit=audit,
            credit_status="blocked",
        )
    if candidate["federal"]["foreign_tax_credit"] != credit:
        raise ValueError("Native credit use and basket/carry allocations do not reconcile.")
    return dict(
        result,
        candidate=candidate,
        basket_audit=audit,
        carry_audit=carry_disposition(case, audit, used),
        credit_status="conditional",
    )


def revision_reasons(case, cash_rows, redetermined_refunds=()):
    year = case.annual.policy.year
    if any(
        r["kind"] == "refund" and r["credit_tax_usd"] and r["credit_year"] != year
        for r in cash_rows
        if r["date"][:4] == str(year) and r["id"] not in redetermined_refunds
    ):
        return ["Original-year credit redetermination requires the closed-return consumer."]
    return []


def payment_snapshot(case, baseline, cash_rows):
    current = [r for r in cash_rows if r["date"][:4] == str(case.annual.policy.year)]
    return dict(
        inputs=case.model_dump(mode="json"),
        baseline=baseline,
        actual_tax_cash=current,
        all_tax_history=cash_rows,
        observed_tax_cash_outflow_usd=sum((r["observed_cash_outflow_usd"] for r in current), ZERO),
        credit_method="Observed paid tax; final2025 ordinary profile",
        unresolved=[],
        candidate=None,
        basket_audit=[],
        carry_audit=None,
        household_funding_supported=False,
    )
