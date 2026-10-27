"""Original unlevered one-year QOF examples isolate actual source gains, returns and tax cash."""

from datetime import date
from decimal import Decimal

from wealthlab.household.scenario import Scenario
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate
from wealthlab.markets.qoz_example import binding, market_case, policy_source
from wealthlab.products.qoz_example import synthetic as native
from wealthlab.tax.projection_example import template


def scenario(months=12):
    if months not in (12, 13):
        raise ValueError("This numeric fixture covers one year or one extra settlement month.")
    data = native(2026).model_dump(mode="json")
    end = date(2026 + months // 12, months % 12 + 1, 1)
    data["end"] = end.isoformat()
    data["incomes"][0]["end"] = end.isoformat()
    linked = data["lot_plan"]
    linked["case"]["end"] = "2026-12-31" if months == 12 else "2027-01-31"
    linked["monthly_marks"] = [
        dict(mark, prices=dict(stock="100")) for mark in linked["monthly_marks"][:months]
    ]
    linked["case"]["closing_prices"] = dict(stock="100")
    plan = data["qoz_plan"]
    plan["observations"] = plan["observations"][:months]
    plan.update(
        sale_requested="2026-12-31",
        sale_not_before="2026-12-31",
        settlement_months=0,
        preferred_hurdle="0",
        carry_fraction="0",
    )
    plan["economics"].update(
        long_multiple="1",
        annual_financing_rate="0",
        annual_manager_fee="0",
        turnover_cost="0",
        exit_cost="0",
    )
    result = policy_source(Scenario.model_validate(data))
    tax = template(result).model_copy(
        update={"federal_wage_withholding": Decimal(0), "nj_wage_withholding": Decimal(0)}
    )
    return result.model_copy(update={"tax_plan": tax})


def case_for(scenario, shocks=None):
    data = market_case(scenario, "deterministic", "early_crash").model_dump(mode="json")
    for asset in data["assets"]:
        asset.update(expected_annual_mark_return=0, annual_volatility=0, annual_cash_yield=0)
    data.update(expected_annual_inflation=0, annual_inflation_volatility=0)
    if shocks:
        data.update(mode="stress", shocks=shocks)
    return MarketCase.model_validate(data)


def flat(months=12, shocks=None):
    household = scenario(months)
    return household, generate(case_for(household, shocks)), binding()
