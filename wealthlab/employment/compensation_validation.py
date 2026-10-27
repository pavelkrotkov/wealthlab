"""Validate supplied allocation scenarios without inferring a private plan's legal tax treatment.

Cash rights and tax recognition require distinct confirmations. Date/sequence
checks protect vesting and forfeiture ordering; owner checks prevent a tranche's
wages from silently entering the other spouse's payroll record.
"""

from wealthlab.employment.compensation_accounts import validate as validate_accounts
from wealthlab.employment.compensation_allocation_audit import validate as validate_audit
from wealthlab.employment.compensation_events import Allocation
from wealthlab.retirement.account_liquidity import validate as validate_locks
from wealthlab.tax.projection_inputs import TaxEvent
from wealthlab.tax.projection_validation import validate as validate_tax
from wealthlab.tax.projection_validation import validate_event


def validate(scenario):
    if scenario.tax_plan is None:
        raise ValueError("Employer compensation requires an explicit household tax plan.")
    validate_tax(scenario.tax_plan, scenario)
    plan = scenario.compensation_plan
    if (
        not plan.tax_inputs_exclude_plan_events_confirmed
        or not plan.all_plan_tax_recognition_supplied_confirmed
    ):
        raise ValueError(
            "Confirm complete supplied plan taxes and no duplicated in-horizon tax inputs."
        )
    validate_records(plan, scenario)
    validate_audit(scenario)
    accounts = {a.id: a for a in scenario.accounts}
    tranches = {t.id: t for t in plan.tranches}
    validate_accounts(scenario, accounts)
    validate_locks(
        plan.liquidity_locks, {t.account for t in plan.tranches}, scenario.start, scenario.end
    )
    validate_events(plan, scenario, accounts, tranches)


def validate_events(plan, scenario, accounts, tranches):
    for event in [*plan.events, *plan.compiled_allocations]:
        if event.tranche not in tranches:
            raise ValueError("Compensation events must name a known tranche.")
        if not scenario.start <= event.date < scenario.end:
            raise ValueError("Compensation events must lie inside the household projection.")
        if isinstance(event, Allocation):
            validate_allocation(event, accounts[tranches[event.tranche].account].owner, scenario)


def validate_records(plan, scenario):
    records = [*plan.tranches, *plan.events, *plan.compiled_allocations, *plan.liquidity_locks]
    identifiers = [r.id for r in records]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Compensation tranche/event IDs must be unique.")
    if any(r.provenance == "unresolved" for r in records):
        raise ValueError("Resolve compensation assumptions before projecting.")
    order = [(e.date, e.sequence) for e in [*plan.events, *plan.compiled_allocations]]
    if len(order) != len(set(order)):
        raise ValueError("Same-day compensation events require distinct explicit sequence numbers.")


def validate_allocation(event, owner, scenario):
    validate_event(
        TaxEvent(
            date=event.date,
            description=event.id,
            cash_received=0,
            federal=event.federal,
            new_jersey=event.new_jersey,
        )
    )
    correct = "wages_primary" if owner == scenario.members[0].id else "wages_spouse"
    if any(
        getattr(event.federal, field)
        for field in ("wages_primary", "wages_spouse")
        if field != correct
    ):
        raise ValueError("Compensation wage recognition must match the tranche owner.")
