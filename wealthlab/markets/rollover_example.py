"""Source and IRA proxies consume the actual direct-transfer household on the same batch."""

from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.wrapper_example import synthetic as wrapper_market
from wealthlab.markets.wrapper_example import wrapper
from wealthlab.retirement.workplace_rollover_example import synthetic as household


def synthetic(mode="deterministic", stress="early_crash"):
    scenario = household()
    _, market, binding = wrapper_market(mode, stress)
    binding = HouseholdBinding.model_validate(
        dict(
            binding.model_dump(exclude={"wrappers"}),
            wrappers=[wrapper(identity) for identity in ("work_pretax", "ira")],
        )
    )
    return scenario, market, binding
