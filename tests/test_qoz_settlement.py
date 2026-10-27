"""Settlement and limited liability preserve actual wealth without duplicate wallet cash."""

from decimal import Decimal

from qoz_cases import flat

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario

D = Decimal


def test_delayed_cash_settles_once_and_retains_wealth_while_pending():
    data = flat(years=2).model_dump(mode="json")
    data["qoz_plan"].update(
        sale_requested="2027-11-30", sale_not_before="2027-12-31", settlement_months=2
    )
    rows = project(Scenario.model_validate(data))
    assert rows[11]["qoz_receivable"] == rows[12]["qoz_receivable"] == D(80000)
    assert rows[13]["qoz_settlement_cash"] == D(80000)
    assert sum(r["qoz_settlement_cash"] for r in rows) == D(80000)
    assert rows[-1]["qoz_nav"] == rows[-1]["qoz_receivable"] == 0


def test_internal_insolvency_cannot_take_shareholder_cash_or_create_household_recourse():
    data = flat().model_dump(mode="json")
    data["qoz_plan"]["economics"]["long_multiple"] = "2"
    data["qoz_plan"]["observations"][1]["asset_return"] = "-1"
    rows = project(Scenario.model_validate(data))
    assert rows[1]["qoz_nav"] == 0
    assert rows[1]["qoz_internal_debt"] == D(80000)
    assert rows[1]["closing_cash"] == D(25000)
    assert rows[1]["net_wealth"] == D(25000)
    assert rows[-1]["qoz_settlement_cash"] == 0
