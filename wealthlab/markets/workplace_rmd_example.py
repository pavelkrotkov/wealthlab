"""Realized plan marks reuse the same complete two-plan RMD household."""

from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.wrapper_example import synthetic as wrapper_market
from wealthlab.markets.wrapper_example import wrapper
from wealthlab.retirement.workplace_rmd_example import synthetic as household


def synthetic(mode="deterministic", stress="early_crash"):
    scenario = household()
    _, market, binding = wrapper_market(mode, stress)
    binding = HouseholdBinding.model_validate(
        dict(
            binding.model_dump(exclude={"wrappers"}),
            wrappers=[wrapper(source) for source in scenario.workplace_plan.products],
        )
    )
    return scenario, market, binding
