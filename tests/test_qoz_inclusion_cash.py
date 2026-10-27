"""Mandatory statutory inclusion can create real tax arrears without investor cash."""

from decimal import Decimal

import pytest
from qoz_cases import flat

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


@pytest.fixture(scope="module")
def mandatory_rows():
    data = flat(years=6).model_dump(mode="json")
    data["members"] = data["members"][:1]
    data["accounts"][0]["balance"] = "0"
    data["lot_plan"]["case"]["lots"][0].update(federal_basis="0", nj_basis="100000")
    data["qoz_plan"]["calls"][0]["amount"] = "100000"
    data["qoz_plan"]["new_jersey"] = "denied"
    for case in data["tax_plan"]["cases"]:
        case["filing"].update(status="single", age_spouse=0)
        case["nj_filing"].update(status="single", age_spouse=0)
    for observation in data["qoz_plan"]["observations"][-2:]:
        observation["locked"] = True
    return project(Scenario.model_validate(data))


def test_five_year_inclusion_has_no_invented_cash(mandatory_rows):
    rows = mandatory_rows
    inclusion = next(r for r in rows if r["date"] == "2032-01-01")
    assert inclusion["qoz_original_gain_included"] == Decimal(90000)
    assert inclusion["qoz_dividends"] == inclusion["qoz_settlement_cash"] == 0


def test_undistributed_nav_cannot_fund_the_actual_tax_bill(mandatory_rows):
    rows = mandatory_rows
    assert rows[-1]["qoz_nav"] == Decimal(100000)
    assert rows[-1]["closing_cash"] == 0
    assert rows[-1]["tax_unfunded"] > 0
    assert rows[-1]["funding_failure"]
