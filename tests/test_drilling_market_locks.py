"""Price marks do not unlock shares or generate commodity sale cash at a zero price."""

from drilling_market_cases import edited

from wealthlab.markets.household_compile import compile_marks
from wealthlab.markets.paths import generate
from wealthlab.products.drilling_market import compare


def test_reference_market_lock_preserves_value_but_blocks_actual_exit_and_joint_funding():
    case = edited(lambda data: data["market"]["shocks"][1].update(lock_months={"reference": 1}))
    result = compare(case)
    shares = result["policies"]["liquid_reference"]
    final = shares["details"][0]["rows"][-1]
    assert (final["drilling_exit_cash"], final["drilling_account_value"]) == (0, 120000)
    assert final["drilling_audit"]["terminal_state"]["reference_exit_pending"] is True
    assert shares["outcomes"][0]["joint_funding_feasible"] is False
    assert result["policies"]["drilling"]["outcomes"][0]["joint_funding_feasible"] is True


def test_entered_reference_lock_is_preserved_when_market_path_is_liquid():
    def configure(data):
        data["household"]["drilling_plan"]["observations"][0]["reference_locked"] = True

    case = edited(configure)
    compiled = compile_marks(case.household, generate(case.market), case.binding, 0)
    assert [r.reference_locked for r in compiled.drilling_plan.observations] == [True, False]


def test_zero_commodity_price_creates_no_production_receipt_without_revaluing_property():
    case = edited(lambda data: data["market"]["shocks"][0]["mark_shocks"].update(commodity=-1))
    result = compare(case)
    final = result["policies"]["drilling"]["details"][0]["rows"][-1]
    assert final["drilling_production_receipts"] == 0
    assert final["drilling_audit"]["terms"]["observations"][-1]["exit_gross_proceeds"] == "40000"
    assert final["drilling_exit_cash"] == 40000
