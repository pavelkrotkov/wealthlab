"""Compile supplied allocations before the household rechecks earnings-sensitive claims.

Only allocation events move into the runtime tax plan; economic events remain
in the tranche book. Original exported inputs are immutable, and a second
preparation cannot recognize the same allocation twice.
"""

from wealthlab.employment.compensation_events import Allocation
from wealthlab.employment.compensation_validation import validate
from wealthlab.tax.projection_inputs import TaxEvent


def prepare(scenario):
    if scenario.compensation_plan is None:
        return scenario
    validate(scenario)
    allocations = [e for e in scenario.compensation_plan.events if isinstance(e, Allocation)]
    if not allocations:
        return scenario
    taxes = [
        TaxEvent(
            date=e.date,
            description=e.id,
            cash_received=0,
            federal=e.federal,
            new_jersey=e.new_jersey,
        )
        for e in allocations
    ]
    events = [e for e in scenario.compensation_plan.events if not isinstance(e, Allocation)]
    return scenario.model_copy(
        update=dict(
            tax_plan=scenario.tax_plan.model_copy(
                update=dict(events=[*scenario.tax_plan.events, *taxes])
            ),
            compensation_plan=scenario.compensation_plan.model_copy(
                update=dict(
                    events=events,
                    compiled_allocations=[
                        *scenario.compensation_plan.compiled_allocations,
                        *allocations,
                    ],
                )
            ),
        )
    )
