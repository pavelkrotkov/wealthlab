"""Real replacement pairs conserve capital; allowed losses are not cash refunds by themselves."""

import pytest

from tests.market_household_cases import flat
from wealthlab.markets.household_run import paired, run
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate
from wealthlab.markets.policy_example import enable


@pytest.fixture(scope="module")
def comparison():
    household, market, binding = flat(cash_yield=0)
    household, binding = enable(household, binding, "Harvesting")
    data = market.model_dump(mode="json")
    data.update(mode="stress", shocks=[dict(name="loss", month=0, mark_shocks=dict(equities=-0.5))])
    batch = generate(MarketCase.model_validate(data))
    harvested = run(household, batch, binding)
    rows = harvested["details"][0]["rows"]
    audit = rows[-1]["lot_audit"]
    retained = household.model_copy(
        update=dict(
            lot_plan=household.lot_plan.model_copy(
                update=dict(
                    case=household.lot_plan.case.model_copy(update=dict(harvest_policies=[]))
                )
            )
        )
    )
    baseline = run(retained, batch, binding)
    return rows, audit, paired(baseline, harvested)[0]


def test_harvesting_uses_actual_sale_cash_and_replacement_basis(comparison):
    rows, audit, _ = comparison
    assert audit["harvest_decisions"][0]["status"] == "harvested"
    replacement = {lot["security_id"]: lot for lot in audit["lots"]}["replacement"]
    assert replacement["federal_basis"] == "30000.00"
    assert rows[-1]["annual_tax"]["federal"]["long_carry"] == 24000


def test_unusable_capital_losses_do_not_create_tax_saving_cash(comparison):
    rows, _, difference = comparison
    assert rows[-1]["net_wealth"] == 51000
    assert sum(r["tax_refund_received"] for r in rows) == 0
    assert difference["real_wealth_change"] == 0
