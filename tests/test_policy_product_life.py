"""Policy closure, protection and actual premium funding remain independent.

A zero-valued in-force contract is not an executed surrender. Conversely, an
actual surrender can close every asset and still fail a separately stated death
protection requirement. Tax and cash reconciliation alone cannot waive it.
"""

from copy import deepcopy

from optimization_cases import changed
from optimization_product_cases import case
from test_policy_product_boundaries import execute

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.markets.option_reporting import outcome
from wealthlab.products.life_household_example import synthetic


def test_zero_value_in_force_policy_does_not_count_as_complete_exit():
    def edit(data):
        policy = data["household"]["life_plan"]["holdings"][0]["contract"]
        policy["events"] = []
        policy["values"].append(dict(policy["values"][-1], date="2027-12-31"))
        for value in policy["values"]:
            value.update(gross_cash_value="0", gross_surrender_value="0", gross_death_benefit="0")

    candidate, result = execute(changed(case(), edit))
    row = result["details"][0]["rows"][-1]
    assert row["account_balances"]["life_policy"] == 0
    assert row["life_policy_values"][0]["closed"] is False
    assert candidate["constraints"]["completed_after_tax_exit"] is False


def test_actual_surrender_cannot_silently_waive_stated_protection_requirement():
    profile = changed(
        case(),
        lambda d: d["household"]["life_plan"]["insurance_need_by_owner"].update(person_a="100000"),
    )
    candidate, result = execute(profile)
    assert candidate["constraints"]["completed_after_tax_exit"]
    assert not candidate["constraints"]["spending_and_product_safety"]
    report = result["outcomes"][0]
    assert report["funded"] and not report["joint_feasible"]
    assert report["life_protection_gap_months"] == 1
    assert report["first_product_failure"] == "2027-12-01"


def test_native_missed_premium_failure_and_coverage_gap_are_both_reported():
    data = synthetic().model_dump(mode="json")
    data["accounts"][0]["balance"] = "600"
    rows = project(Scenario.model_validate(data))
    report = outcome(rows, False)
    assert report["life_payment_failure_months"] == 1
    assert report["life_protection_gap_months"] == 3
    assert not report["product_feasible"]
    without_coverage = deepcopy(rows)
    for row in without_coverage:
        row["life_protection_shortfall"] = 0
    assert outcome(without_coverage, False)["life_payment_failure_months"] == 1
    assert not outcome(without_coverage, False)["life_feasible"]
