"""Dated prices and sale permission cannot use future marks or unavailable assets.

Cash targets raise cash inside the HSA, not a recipient distribution. Selected
liquid shares and actual proceeds determine how much cash can be made available.
Quotes carry full security coverage; a later closing quote is never used early.
"""

from datetime import timedelta


def validate_prices(plan):
    securities = {s.id for s in plan.case.securities}
    if set(plan.opening_prices) != securities:
        raise ValueError("Supply an opening HSA price for every security.")
    dates = [m.date for m in plan.marks]
    if dates != sorted(set(dates)):
        raise ValueError("HSA mark dates must be unique and chronological.")
    for mark in plan.marks:
        validate_mark(mark, plan.case, securities)


def validate_mark(mark, case, securities):
    if not case.as_of <= mark.date <= case.end or set(mark.prices) != securities:
        raise ValueError("HSA marks need complete prices and in-horizon dates.")
    if mark.date == case.end and mark.prices != case.closing_prices:
        raise ValueError("A dated final HSA mark must match the declared closing prices.")


def validate_sources(plan):
    accounts = {a.id for a in plan.case.accounts}
    securities = {s.id for s in plan.case.securities}
    keys = [(s.account_id, s.security_id) for s in plan.funding_sources]
    if len(keys) != len(set(keys)):
        raise ValueError("HSA cash-raising sources must be unique account/security pairs.")
    if any(a not in accounts or s not in securities for a, s in keys):
        raise ValueError("HSA cash-raising sources require known accounts and securities.")


def validate_events(plan):
    case = plan.case
    accounts, securities = {a.id for a in case.accounts}, {s.id for s in case.securities}
    for target in plan.cash_targets:
        if target.account_id not in accounts or not case.as_of <= target.date <= case.end:
            raise ValueError("HSA cash targets need known accounts and in-horizon dates.")
        if target.provenance == "unresolved":
            raise ValueError("Resolve HSA cash-target assumptions.")
    for lock in plan.liquidity_locks:
        validate_lock(lock, case, securities)


def validate_lock(lock, case, securities):
    if lock.security_id not in securities or not case.as_of <= lock.start < lock.end:
        raise ValueError("HSA security locks need a known security and positive in-horizon range.")
    if lock.end > case.end + timedelta(days=1):
        raise ValueError("HSA security lock extends past the projection.")
    if lock.provenance == "unresolved":
        raise ValueError("Resolve HSA security-lock assumptions.")
