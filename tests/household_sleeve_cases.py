"""Flat zero-fee sleeves isolate actual household transfers, insolvency and recognition."""

from wealthlab.household.scenario import Scenario
from wealthlab.products.household_example import synthetic


def flat(cash=10000):
    data = synthetic().model_dump(mode="json")
    data.update(end="2027-01-01", incomes=[], expenses=[])
    data["accounts"][0]["balance"] = str(cash)
    data["tax_plan"]["income_rules"] = []
    data["tax_plan"]["cases"] = data["tax_plan"]["cases"][:1]
    sleeve = data["sleeve_plan"]["sleeves"][0]
    sleeve["observations"] = sleeve["observations"][:12]
    sleeve["allocations"] = []
    sleeve["case"].update(
        annual_borrow_rate=0,
        annual_financing_rate=0,
        annual_manager_fee=0,
        turnover_cost=0,
        exit_cost=0,
        rebalance="none",
        exit_at_horizon=False,
    )
    return Scenario.model_validate(data)


def change(household, modify):
    data = household.model_dump(mode="json")
    modify(data)
    return Scenario.model_validate(data)
