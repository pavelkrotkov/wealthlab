"""Original flat cash-funded option/life choices share one actual terminal-year advisory bill."""

from tests.optimization_option_cases import case as options
from wealthlab.optimization.advisory_example import extend as advisory
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.new_life_example import extend as life


def case():
    data = advisory(life(options())).model_dump(mode="json")
    schedule = data["household"]["advisory_fee_plan"]["schedules"][0]
    schedule.update(
        source_ref="Original one-year terminal advisory invoice; no 2026 fee engagement assumed",
        tiers=[dict(upper_limit=None, annual_rate=".01")],
        day_count=365,
        periods=[
            dict(
                accrual_start="2027-01-01",
                accrual_end="2028-01-01",
                valuation_date="2027-12-31",
                assessment_date="2027-12-31",
                payment_due_date="2027-12-31",
            )
        ],
    )
    return PolicySearch.model_validate(data)


def selection(case, units, policy):
    return [
        case.dimensions[0].choices[0],
        next(c for c in case.dimensions[1].choices if c.option_units == units),
        next(c for c in case.dimensions[2].choices if bool(c.new_life_purchases) == policy),
    ]
