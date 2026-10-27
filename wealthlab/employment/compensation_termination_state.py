"""Conditional supplied termination evidence, independent from actual tax settlement."""

from wealthlab.employment.compensation_termination_checks import actual, facts, missing


def observed(ledger, tranche, end, account_reconciles):
    # Only already-applied native events are candidates; a future declaration
    # cannot certify today's exit or deposit its hypothetical proceeds.
    record, event = latest(ledger, tranche.id)
    if event is None:
        return {}
    unknown = missing(event, end)
    reasons = (
        [] if unknown else facts(event) + actual(ledger, tranche, record, event, account_reconciles)
    )
    # The before-state prevents a later payout from retrospectively validating
    # an earlier termination. Incomplete source facts remain explicit unknowns.
    result: dict = supplied(event, not unknown)
    pending = pending_allocations(ledger, tranche.id, end)
    result.update(
        contractual_exit_proven=None if unknown else not reasons,
        termination_status=status(unknown, reasons),
        termination_reasons=unknown or reasons,
        termination_event=event.model_dump(mode="json"),
        actual_balances_at_termination=dict(record["before"]),
        conditional_on_supplied_facts=True,
        legal_verification_performed=False,
        future_supplied_tax_allocations=pending,
        future_supplied_tax_allocations_clear=not pending,
        tax_scope="Tax settlement stays in TaxLedger; termination creates no tax exemption",
    )
    return result


def supplied(event, available):
    return dict(
        quantities_known=available and event.remaining_units is not None,
        contract_units=event.remaining_units if available else None,
        separate_deferred_value=event.remaining_deferred_value if available else None,
        separate_deferred_rights_known=available and event.remaining_deferred_value is not None,
        remaining_contract_cash_due=event.remaining_cash_due if available else None,
        future_rights_after_horizon=remaining(event.no_future_rights, available),
        future_contract_obligations_after_horizon=remaining(
            event.no_future_contract_obligations, available
        ),
        deferred_scope="Supplied contractual units/deferred-right facts; no value-based inference",
    )


def remaining(no_remaining, available):
    return None if no_remaining is None or not available else not no_remaining


def status(unknown, reasons):
    if unknown:
        return "unresolved"
    return "not_reconciled" if reasons else "conditional_supplied_exit"


def pending_allocations(ledger, tranche_id, end):
    # Legal closure never establishes actual tax settlement; compiled source
    # allocations remain visible even though economic-event preparation moved them.
    raw = [event for event in ledger.events if event.kind == "allocation"]
    return [
        event.model_dump(mode="json")
        for event in [*ledger.plan.compiled_allocations, *raw]
        if event.tranche == tranche_id and event.date >= end
    ]


def latest(ledger, tranche_id):
    records = [
        row for row in ledger.log if row["tranche"] == tranche_id and row["kind"] == "termination"
    ]
    if not records:
        return None, None
    record = records[-1]
    event = next(item for item in ledger.events if item.id == record["event"])
    return record, event
