"""Small complete synthetic cases isolate actual bills from optional income and elections."""

from wealthlab.household.scenario import Scenario
from wealthlab.retirement.medical_bill_example import synthetic


def data(cash=1000, hsa=3000, **bill):
    value = synthetic().model_dump(mode="json")
    value["accounts"][0]["balance"] = str(cash)
    value["accounts"][1]["balance"] = str(hsa)
    value["tax_plan"]["events"] = []
    plan = value["hsa_plan"]
    plan["contributions"], plan["withdrawals"] = [], []
    plan["medical_bills"][0].update(bill)
    return value


def case(cash=1000, hsa=3000, **bill):
    return Scenario.model_validate(data(cash, hsa, **bill))
