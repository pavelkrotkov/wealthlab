"""Supplied closure facts cannot override actual dollars, source timing or new grants."""

FACTS = (
    "source_date",
    "contract_terminated",
    "remaining_units",
    "remaining_deferred_value",
    "remaining_cash_due",
    "no_future_rights",
    "no_future_contract_obligations",
    "exit_tax_recognition_supplied",
)
ZERO_FACTS = ("remaining_units", "remaining_deferred_value", "remaining_cash_due")
YES_FACTS = (
    "contract_terminated",
    "no_future_rights",
    "no_future_contract_obligations",
    "exit_tax_recognition_supplied",
)


def missing(event, end):
    # Unset amounts/booleans never acquire favorable zero/true defaults.
    reasons = [
        f"Missing supplied termination fact: {field}"
        for field in FACTS
        if getattr(event, field) is None
    ]
    if not event.source_reference.strip() or not event.unit_label.strip():
        reasons.append("Provide a source reference and the contractual unit definition.")
    if event.source_date is not None and event.source_date >= end:
        reasons.append("Termination source is not available before the observation cutoff.")
    return reasons


def facts(event):
    reasons = [
        f"Supplied {field} is not zero." for field in ZERO_FACTS if getattr(event, field) != 0
    ]
    reasons += [
        f"Supplied {field} is not confirmed true."
        for field in YES_FACTS
        if getattr(event, field) is not True
    ]
    return reasons


def actual(ledger, tranche, record, event, account_reconciles):
    reasons = []
    if any(record["before"].values()):
        reasons.append("Termination cannot remove actual vested or unvested dollar balances.")
    if any(ledger.states[tranche.id].values()) or not account_reconciles:
        reasons.append("Actual remaining tranche/account balances do not reconcile to an exit.")
    if grants_after(ledger, tranche.id, event):
        reasons.append("A later positive grant contradicts no remaining contractual rights.")
    return reasons


def grants_after(ledger, tranche_id, event):
    key = (event.date, event.sequence)
    return [
        item.id
        for item in ledger.events
        if item.tranche == tranche_id
        and item.kind == "grant"
        and item.amount > 0
        and (item.date, item.sequence) > key
    ]
