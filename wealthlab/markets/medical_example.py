"""Inflated bills test spending safety while HSA election bounds remain explicit."""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_example import synthetic as market_example
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.retirement.medical_bill_example import synthetic as household_example


def synthetic(mode="deterministic", stress="early_crash"):
    data = household_example().model_dump(mode="json")
    data["name"] = "Synthetic medical cost inflation and bounded HSA election"
    data["accounts"][0]["balance"] = "2000"
    data["accounts"][1]["balance"] = "6000"
    data["tax_plan"]["events"] = []
    plan = data["hsa_plan"]
    plan["contributions"], plan["withdrawals"] = [], []
    plan["medical_bills"][0].update(incurred="2027-01-10", date="2027-01-15")
    household = Scenario.model_validate(data)
    _, market, binding = market_example(mode, stress)
    market = market.model_copy(update=dict(expected_annual_inflation=0.20))
    config = binding.model_dump(exclude={"securities"})
    config["medical_bill_inflation"] = [
        dict(
            bill_id="care", amount_basis="projection_start_prices", hsa_election="keep_nominal_cap"
        )
    ]
    return household, market, HouseholdBinding.model_validate(config)
