"""Actual invested-HSA medical funding on original synthetic common market paths."""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_example import synthetic as market_example
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.retirement.hsa_invested_example import synthetic as household_example


def synthetic(mode="deterministic", stress="early_crash"):
    data = household_example().model_dump(mode="json")
    data["name"] = "Synthetic invested HSA medical funding on market paths"
    # A December bill uses observed prior monthly marks. Both election and
    # cost stay nominal here; separate medical CPI bindings remain available.
    data["hsa_plan"]["medical_bills"][0].update(incurred="2026-12-10", date="2026-12-15")
    household = Scenario.model_validate(data)
    _, market, original = market_example(mode, stress)
    market_data = market.model_dump(mode="json")
    market_data["end"] = data["end"]
    market_data["shocks"] = [s for s in market_data["shocks"] if s["month"] < 12]
    if mode == "historical":
        market_data["historical"]["months"] = market_data["historical"]["months"][:12]
    market = type(market).model_validate(market_data)
    binding = original.model_dump(exclude={"securities"})
    binding.update(
        hsa_securities=[dict(security_id="fund", factor="equities", nj_cash_character="dividends")],
        replace_hsa_observations_confirmed=True,
    )
    return household, market, HouseholdBinding.model_validate(binding)
