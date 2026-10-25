"""Preserved source allocations reconcile exactly to compiled zero-cash TaxPlan events."""

from wealthlab.tax.projection_inputs import TaxEvent


def validate(scenario):
    for allocation in scenario.compensation_plan.compiled_allocations:
        expected = TaxEvent(
            date=allocation.date,
            description=allocation.id,
            cash_received=0,
            federal=allocation.federal,
            new_jersey=allocation.new_jersey,
        )
        matches = [
            event
            for event in scenario.tax_plan.events
            if event.description == allocation.id and event.date == allocation.date
        ]
        if matches != [expected]:
            raise ValueError(
                "Compiled employer allocation must match exactly one zero-cash TaxEvent."
            )
