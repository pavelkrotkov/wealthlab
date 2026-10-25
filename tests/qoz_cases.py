"""Small actual-wallet scenarios; no mock tax or product calculations."""

from datetime import date, timedelta

from wealthlab.household.scenario import Scenario
from wealthlab.products.qoz_example import synthetic


def flat(year=2027, years=1):
    data = synthetic(year).model_dump(mode="json")
    end = date(year + years, 1, 1)
    data.update(end=end.isoformat(), incomes=[])
    data["tax_plan"]["income_rules"] = []
    data["tax_plan"]["cases"] = data["tax_plan"]["cases"][:years]
    linked, plan = data["lot_plan"], data["qoz_plan"]
    linked["case"]["end"] = (end - timedelta(days=1)).isoformat()
    linked["monthly_marks"] = linked["monthly_marks"][: years * 12]
    linked["case"]["closing_prices"] = linked["monthly_marks"][-1]["prices"]
    plan["observations"] = plan["observations"][: years * 12]
    for row in plan["observations"]:
        row["asset_return"] = "0"
    plan["economics"].update(
        long_multiple="1",
        annual_financing_rate="0",
        annual_manager_fee="0",
        maintenance_fraction_of_gross="0",
    )
    plan.update(
        preferred_hurdle="0",
        carry_fraction="0",
        sale_requested=f"{year + years - 1}-11-30",
        sale_not_before=f"{year + years - 1}-12-31",
        settlement_months=0,
    )
    return Scenario.model_validate(data)


def edited(scenario, **changes):
    data = scenario.model_dump(mode="json")
    data["qoz_plan"].update(changes)
    return Scenario.model_validate(data)
