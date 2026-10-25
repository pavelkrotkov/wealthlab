"""Reserved collateral cannot fund spending; dividends and loans retain actual cash semantics."""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.products.option_household_example import synthetic


def test_uncovered_broker_collateral_consumes_actual_cash_and_can_fail_spending():
    data = synthetic().model_dump(mode="json")
    data["option_plan"]["case"].update(cover_stock_calls=False, short_collateral_fraction="0.5")
    rows = project(Scenario.model_validate(data))
    assert rows[0]["closing_cash"] == 0
    assert rows[0]["option_margin_unfunded"] > 0
    assert rows[0]["funding_failure"]
    assert rows[0]["essential_unfunded"] == 500


def test_actual_ordinary_dividend_cash_is_recognized_without_duplicate_receipt():
    data = synthetic().model_dump(mode="json")
    data["option_plan"]["case"]["dividends"] = [
        dict(ex_date="2026-01-31", pay_date="2026-01-31", per_share="1")
    ]
    data["option_plan"]["ordinary_dividend_tax_on_cash_receipt_confirmed"] = True
    rows = project(Scenario.model_validate(data))
    assert rows[-1]["closing_cash"] == 6600
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 6600
    assert rows[-1]["annual_tax"]["new_jersey"]["gross_income"] == 5600


def test_physical_purchase_uses_actual_household_cash_and_retains_two_tax_bases():
    data = synthetic().model_dump(mode="json")
    data["accounts"][0]["balance"] = "20000"
    case = data["option_plan"]["case"]
    case["legs"][0].update(side="long", strike="100")
    case["unwind"] = False
    rows = project(Scenario.model_validate(data))
    assert rows[1]["option_shares"] == 200
    assert rows[1]["option_federal_basis"] == 15500
    assert rows[1]["option_nj_basis"] == 16500
    assert rows[-1]["closing_cash"] == 3500
