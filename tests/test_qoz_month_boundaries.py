"""Observed partial-month marks cannot masquerade as supported statutory month ends."""

from datetime import date
from types import SimpleNamespace

import pytest
from qoz_cases import flat

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.products.qoz_dates import validate_horizon


def test_partial_final_month_is_rejected_even_with_matching_source_and_product_snapshots():
    data = flat().model_dump(mode="json")
    data["end"] = "2027-06-15"
    linked, plan = data["lot_plan"], data["qoz_plan"]
    linked["case"]["end"] = "2027-06-14"
    linked["monthly_marks"] = linked["monthly_marks"][:6]
    linked["monthly_marks"][-1]["date"] = "2027-06-14"
    plan["observations"] = plan["observations"][:6]
    plan["observations"][-1]["date"] = "2027-06-14"
    plan.update(sale_requested="2027-06-14", sale_not_before="2027-06-14")
    with pytest.raises(ValueError, match="whole calendar months"):
        project(Scenario.model_validate(data))


def test_thirty_year_gate_uses_the_actual_anniversary_inside_the_exclusive_horizon():
    call = SimpleNamespace(date=date(2028, 6, 30))
    plan = SimpleNamespace(calls=[call])
    validate_horizon(SimpleNamespace(end=date(2058, 1, 1)), plan)
    with pytest.raises(ValueError, match="Thirty-year"):
        validate_horizon(SimpleNamespace(end=date(2058, 7, 1)), plan)
