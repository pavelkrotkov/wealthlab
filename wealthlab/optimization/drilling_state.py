"""Missing, nonfinite and malformed native audit values cannot certify book closure."""

from decimal import Decimal, InvalidOperation


def zero(value):
    if isinstance(value, bool):
        return False
    try:
        number = Decimal(value)
        return number.is_finite() and number == 0
    except (TypeError, ValueError, InvalidOperation):
        return False


def zeros(values, required):
    return (
        isinstance(values, dict)
        and set(required) <= values.keys()
        and all(zero(value) for value in values.values())
    )


def ending_state(plan, audit, row):
    if not isinstance(audit, dict) or audit.get("future_tax_events") != []:
        return None
    state = audit.get("terminal_state")
    if not isinstance(state, dict) or state.get("mode") != plan.mode:
        return None
    balances = row.get("account_balances")
    if not isinstance(balances, dict):
        return None
    if not zero(balances.get(plan.account_id)) or not zero(state.get("call_owed")):
        return None
    return state
