"""Generated source prices decide eligible gains without standalone quote overrides."""

from decimal import Decimal

from tests.qoz_market_cases import flat
from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_run import run


def test_actual_month_end_source_policy_ignores_irrelevant_supplied_quote():
    shocks = [dict(name="source growth", month=0, mark_shocks=dict(source_stock=0.1))]
    case, batch, binding = flat(shocks=shocks)
    data = case.model_dump(mode="json")
    data["lot_plan"]["case"]["sale_policies"][0]["prices"]["stock"] = "999"
    final = run(Scenario.model_validate(data), batch, binding)["details"][0]["rows"][-1]
    disposal = final["lot_audit"]["disposals"][0]
    assert disposal["proceeds"] == 110000
    assert (disposal["federal_gross_gain"], disposal["nj_gross_gain"]) == (90000, 80000)
    assert final["qoz_audit"]["calls"][0]["funded"] == 80000
    # $10k source-price gain adds tax, rather than becoming an invented full deferral.
    assert final["annual_tax"]["total_liability"] == Decimal("20473.50")
    assert final["closing_cash"] == Decimal("166526.50")
