"""A corrected return changes future lookback bills without rewriting cash history.

The synthetic return crosses the frozen-2026 joint tier boundary: $235k
provisionally and $215k after the loss. Normal two-year lookbacks must use
the finalized return in 2028. A matched case with no loss stays in tier one;
current premium cash is neither refunded nor retroactively removed.
"""

from copy import deepcopy
from datetime import date, timedelta

from tests.january_consumer_cases import data
from wealthlab.household.calendar import months
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.medicare_household_template import template


def case():
    result = data(175000)
    result["end"] = "2029-01-01"
    annual = result["tax_plan"]["cases"][-1]
    added = deepcopy(annual)
    added["policy"]["year"] = 2028
    for key in ("age_primary", "age_spouse"):
        added["filing"][key] += 1
    result["tax_plan"]["cases"].append(added)
    linked = result["lot_plan"]
    linked["case"]["end"] = "2028-12-31"
    linked["monthly_marks"].extend(
        dict(date=(end - timedelta(days=1)).isoformat(), prices=dict(stock="130"))
        for start, end in months(date(2028, 1, 1), date(2029, 1, 1))
    )
    for index, member in enumerate(result["members"]):
        member["birth_date"] = f"{1960 + index}-01-01"
    for annual in result["tax_plan"]["cases"]:
        annual["filing"]["age_primary"] = annual["policy"]["year"] - 1960
        annual["filing"]["age_spouse"] = annual["policy"]["year"] - 1961
    scenario = Scenario.model_validate(result)
    result["medicare_plan"] = template(scenario)
    coverage = result["medicare_plan"]["case"]
    coverage["complete_context"] = True
    for row in coverage["coverage"]:
        row["eligibility_confirmed"] = True
    for flag in (
        "direct_billing_without_benefit_withholding_confirmed",
        "costs_excluded_from_other_expenses_confirmed",
        "complete_household_tax_history_confirmed",
    ):
        result["medicare_plan"][flag] = True
    return result


def test_january_final_income_drives_two_year_lookback_premiums():
    result = project(Scenario.model_validate(case()))
    bills = result[-1]["medicare_audit"]["bills"]
    future = [b for b in bills if b["date"].year == 2028]
    assert future and all(b["income_year"] == 2026 for b in future)
    assert all(b["magi"] == 215000 and b["tier"] == 0 for b in future)
    baseline = case()
    baseline["lot_plan"]["case"]["trades"] = []
    uncorrected = project(Scenario.model_validate(baseline))[-1]["medicare_audit"]["bills"]
    assert all(b["tier"] == 1 for b in uncorrected if b["date"].year == 2028)
