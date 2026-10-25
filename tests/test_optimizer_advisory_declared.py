"""Zero-opening product accounts stay in fee scope even when entry is declined.

The parent optimizer owns these offer interfaces. The fee consumer validates the
native plan/account contract without implementing its investment or tax choices.
"""

from types import SimpleNamespace

import pytest

from wealthlab.household.advisory_example import plan
from wealthlab.household.scenario import Scenario
from wealthlab.optimization.advisory_fees import validate
from wealthlab.products.drilling_example import synthetic as drilling
from wealthlab.products.qoz_example import synthetic as qoz


@pytest.fixture(params=[(drilling, "drilling"), (qoz, "qoz")])
def offered(request):
    build, field = request.param
    household = build()
    household = household.model_copy(update={"advisory_fee_plan": plan(household)})
    native = getattr(household, field + "_plan")
    model = SimpleNamespace(
        household=household,
        sleeve_opportunities=[],
        life_opportunities=[],
        new_life_opportunities=[],
        exchange_opportunities=[],
        option_opportunity=None,
        **{field + "_offers": [SimpleNamespace(plan=None), SimpleNamespace(plan=native)]},
    )
    return model, native.account_id


def test_present_zero_product_account_keeps_required_source_coverage(offered):
    model, account_id = offered
    account = next(a for a in model.household.accounts if a.id == account_id)
    assert account.balance == 0
    validate(model)
    schedule = model.household.advisory_fee_plan.schedules[0]
    assert next(r for r in schedule.covered if r.account_id == account_id).presence == "required"


def test_inactive_offer_cannot_erase_original_zero_account_fee_scope(offered):
    model, account_id = offered
    data = model.household.model_dump(mode="json")
    schedule = data["advisory_fee_plan"]["schedules"][0]
    schedule["covered"] = [r for r in schedule["covered"] if r["account_id"] != account_id]
    model.household = Scenario.model_validate(data)
    with pytest.raises(ValueError, match="explicitly name every strategy"):
        validate(model)
