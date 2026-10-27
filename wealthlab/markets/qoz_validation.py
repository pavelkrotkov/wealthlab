"""A native QOF book may use only its explicit exact path and net-entity-tax asset convention."""

from datetime import timedelta

import numpy as np

from wealthlab.household.calendar import months
from wealthlab.markets.qoz_compile import observations
from wealthlab.products.qoz_dates import validate_dates
from wealthlab.products.qoz_validation import validate_observations


def validate(scenario, batch, binding, index):
    selected = binding.qoz
    if scenario.qoz_plan is None:
        if selected is not None:
            raise ValueError("A QOZ market binding needs an actual native QOZ plan.")
        return
    validate_binding(selected, scenario.qoz_plan.account_id, batch)
    if not 0 <= index < len(batch.mark_returns):
        raise ValueError("QOZ path index lies outside the realized batch.")
    # Complete observed month ends and the native tax/lock calendar are checked
    # before any linked sale or call can move cash. No missing months are filled.
    expected = [end - timedelta(days=1) for _, end in months(scenario.start, scenario.end)]
    validate_observations(scenario.qoz_plan, expected)
    compiled = observations(scenario, batch, binding, index)
    plan = scenario.qoz_plan.model_copy(update={"observations": compiled})
    validate_observations(plan, expected)
    validate_dates(scenario, plan, expected)


def validate_binding(selected, account_id, batch):
    if selected is None or selected.account_id != account_id:
        raise ValueError("Bind the complete native QOZ account to one explicit asset factor.")
    if not (
        selected.net_entity_tax_pre_investor_cost_confirmed
        and selected.replace_dated_asset_returns_confirmed
    ):
        raise ValueError(
            "Confirm net entity-tax/pre-investor-cost returns and replacement observations."
        )
    if not selected.return_source_description.strip() or selected.factor not in batch.assets:
        raise ValueError("QOZ needs a nonempty return source and a known asset factor.")
    factor = batch.assets.index(selected.factor)
    if np.any(batch.cash_yields[:, :, factor] != 0):
        raise ValueError(
            "QOZ asset factors require zero separate cash yield; native dividends are retained."
        )


def validate_execution(scenario, execution):
    if scenario.qoz_plan is None and execution.binding.qoz is None:
        return
    validate(scenario, execution.batch, execution.binding, execution.index)
    expected = observations(scenario, execution.batch, execution.binding, execution.index)
    if scenario.qoz_plan.observations != expected:
        raise ValueError(
            "Compile QOZ observations from this exact realized path; stale returns are blocked."
        )
