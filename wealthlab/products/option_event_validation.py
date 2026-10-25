"""Termination/roll chronology must be supplied without inferred early assignment."""


def validate_events(case, dates):
    legs = {leg.id: leg for leg in case.legs}
    if len({event.leg_id for event in case.events}) != len(case.events):
        raise ValueError("Split partial quantities into legs; each leg terminates at most once.")
    for event in case.events:
        leg = legs.get(event.leg_id)
        if leg is None or event.date not in dates:
            raise ValueError("Termination must reference a known leg and dated mark.")
        validate_event(event, leg)
        validate_roll(event, leg, legs)
    validate_roll_coverage(case)
    validate_roll_targets(case.legs)


def validate_event(event, leg):
    """Exercise style constrains the dated scenario, not the exercise probability.

    A supplied close quote describes the actual trade, while expiry uses intrinsic.
    """
    if not leg.opened <= event.date <= leg.expiry:
        raise ValueError("Termination must be within the option's life.")
    validate_quote(event)
    if event.action == "expire" and event.date != leg.expiry:
        raise ValueError("An option can expire only at its contractual expiry.")
    early_european = event.action == "exercise" and leg.style == "european"
    if early_european and event.date != leg.expiry:
        raise ValueError("European options cannot be exercised early.")


def validate_quote(event):
    if event.action == "close" and event.close_price is None:
        raise ValueError("Closing transactions require an explicit per-unit execution price.")
    if event.action != "close" and event.close_price is not None:
        raise ValueError("Only a closing transaction accepts an execution price.")


def validate_roll(event, leg, legs):
    if leg.rolls_to and (event.action != "close" or legs[leg.rolls_to].opened != event.date):
        raise ValueError("Rolls close the old leg and separately open the target that day.")


def validate_roll_coverage(case):
    missing = {leg.id for leg in case.legs if leg.rolls_to} - {e.leg_id for e in case.events}
    if missing:
        raise ValueError("Each configured roll needs an explicit close transaction.")


def validate_roll_targets(legs):
    from graphlib import CycleError, TopologicalSorter

    targets = [leg.rolls_to for leg in legs if leg.rolls_to]
    if len(targets) != len(set(targets)):
        raise ValueError("Each roll target must have exactly one incoming roll.")
    graph = {leg.id: [leg.rolls_to] if leg.rolls_to else [] for leg in legs}
    try:
        TopologicalSorter(graph).prepare()
    except CycleError as error:
        raise ValueError("Roll targets must be separate, acyclic contracts.") from error
