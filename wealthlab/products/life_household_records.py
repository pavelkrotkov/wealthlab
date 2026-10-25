"""Validate supplied failure exits and withholding before they can change household cash."""

from wealthlab.products.life_contract_tax import TERMINAL
from wealthlab.products.life_illustration_flows import OUTFLOWS


def validate_values(value):
    amounts = (value.gross_cash_value, value.gross_surrender_value, value.gross_death_benefit)
    if any(amount is None for amount in amounts):
        raise ValueError("Household policy cash, surrender and death values must be supplied.")


def validate_events(scenario, holding):
    events = {e.id: e for e in holding.contract.events}
    if set(holding.withholding) - set(events) or set(holding.failure_exits) - set(events):
        raise ValueError("Policy withholding/failure exits must name existing scheduled events.")
    validate_required_exits(scenario, holding, events.values())
    for event_id in holding.withholding:
        if events[event_id].kind in OUTFLOWS | {"capitalized_interest"}:
            raise ValueError("Policy source withholding requires actual received cash.")


def validate_required_exits(scenario, holding, events):
    """An unpaid premium cannot silently retain the fully funded illustration.

    These exits are supplied conditional settlements, not an inferred grace period
    or a promise that the insurer allows cash surrender on the missed due date.
    """
    for event in events:
        if scenario.start <= event.date < scenario.end and event.kind in OUTFLOWS:
            failure = holding.failure_exits.get(event.id)
            if failure is None:
                raise ValueError("Each required policy payment needs a supplied failure exit.")
            validate_failure(event, failure)


def validate_failure(trigger, failure):
    event = failure.event
    if not failure.applicable_to_unfunded_payment_confirmed:
        raise ValueError(
            "Confirm the supplied failure settlement applies after an unfunded payment."
        )
    if event.kind not in TERMINAL or event.date != trigger.date:
        raise ValueError(
            "A policy failure exit must be a full settlement on the failed payment date."
        )
    if event.nj_ordinary_income is None or event.provenance == "unresolved":
        raise ValueError("Policy failure settlement and NJ recognition must be resolved inputs.")


def validate_ownership(scenario):
    owned = {h.account_id for h in scenario.life_plan.holdings} if scenario.life_plan else set()
    accounts = {a.id for a in scenario.accounts if a.wrapper == "insurance"}
    if owned != accounts:
        raise ValueError("Every insurance account must have exactly one policy holding.")
