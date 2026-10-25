"""Reject inconsistent histories rather than inventing continuation or loan terms."""

from wealthlab.products.life_contract_history import validate_dates, validate_events
from wealthlab.products.life_contract_tax import TERMINAL


def validate(contract):
    if contract.provenance == "unresolved":
        raise ValueError("Resolve the policy source and executed opening snapshot before modeling.")
    if not contract.owner_birth_date < contract.issue_date <= contract.start:
        raise ValueError("Owner birth, issue and opening dates must be ordered.")
    if contract.stop_funding_date is not None and contract.stop_funding_date < contract.issue_date:
        raise ValueError("The premium stop date cannot precede issue.")
    validate_events(contract.events)
    validate_dates(contract)
    validate_termination(contract)


def validate_termination(contract):
    terminal = [e for e in contract.events if e.kind in TERMINAL]
    if terminal and terminal != contract.events[-1:]:
        raise ValueError("No policy event can follow a full surrender or confirmed lapse.")
    if terminal and any(v.date >= terminal[0].date for v in contract.values):
        raise ValueError("Supply in-force values only before termination; closed value is zero.")
    validate_stop(contract)


def validate_stop(contract):
    if contract.stop_funding_date is None:
        return
    for event in contract.events:
        if event.kind == "premium" and event.date > contract.stop_funding_date:
            raise ValueError("Actual premiums cannot follow the selected stop-funding date.")
