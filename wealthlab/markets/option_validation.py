"""Bounded monthly option execution refuses unavailable dates, prices and liquidity paths."""

from wealthlab.markets.option_compile import marks
from wealthlab.markets.option_dates import validate_dates
from wealthlab.markets.option_returns import validate_returns


def validate(scenario, batch, binding):
    selected = binding.options
    if scenario.option_plan is None:
        if selected is not None:
            raise ValueError("An option binding requires an actual household option plan.")
        return
    factors = validate_binding(selected, scenario.option_plan.account_id, batch.assets)
    validate_returns(batch, factors)
    validate_dates(scenario)


def validate_execution(scenario, execution):
    if not all(hasattr(execution, key) for key in ("batch", "binding", "index")):
        raise ValueError(
            "Unconfirmed generated market binding; an explicit option adapter is required."
        )
    validate(scenario, execution.batch, execution.binding)
    expected = marks(scenario, execution.batch, execution.binding.options, execution.index)
    if scenario.option_plan.case.marks != expected:
        raise ValueError(
            "Compile option prices from this exact realized path; stale marks are blocked."
        )


def validate_binding(selected, account_id, assets):
    if selected is None or selected.account_id != account_id:
        raise ValueError("Bind the complete actual option account to explicit stock/index factors.")
    if not (
        selected.replace_dated_marks_confirmed and selected.hypothetical_model_execution_confirmed
    ):
        raise ValueError(
            "Confirm replacement marks and hypothetical execution; these are not option quotes."
        )
    factors = {selected.stock_factor, selected.index_factor}
    if len(factors) != 2 or not factors <= set(assets):
        raise ValueError("Options require two distinct known stock/index factors.")
    return factors
