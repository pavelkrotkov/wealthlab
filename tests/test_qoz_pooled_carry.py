"""Pooled carry weights actual subscription dates instead of backdating later capital.

At 12% simple preferred hurdle, $100k invested for 365 days earns a $12k hurdle,
while $50k invested for 184 days earns $3,024.66. At $200k ending NAV, 20% carry
above capital plus that hurdle is $6,995.07, never a promised cash yield.
"""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from qoz_cases import flat

from wealthlab.products.qoz_economics import create, sell, step, subscribe


def test_pooled_carry_does_not_treat_later_cash_as_invested_on_the_first_call_date():
    plan = flat().qoz_plan.model_copy(
        update=dict(preferred_hurdle=Decimal(".12"), carry_fraction=Decimal(".20"))
    )
    fund = create(plan, Decimal(100000), date(2027, 1, 31))
    subscribe(fund, Decimal(50000), date(2027, 7, 31))
    step(fund, SimpleNamespace(date=date(2028, 1, 31), asset_return=Decimal(1) / 3, locked=False))
    result = sell(fund, plan, date(2028, 1, 31))
    assert result["carry"] == Decimal("6995.07")
    assert result["proceeds"] == Decimal("193004.93")


def test_carry_uses_actual_sale_cash_after_selling_cost_before_its_own_charge():
    plan = flat().qoz_plan
    case = plan.economics.model_copy(update=dict(exit_cost=Decimal(".02")))
    plan = plan.model_copy(update=dict(economics=case, carry_fraction=Decimal(".20")))
    fund = create(plan, Decimal(80000), date(2027, 1, 31))
    step(fund, SimpleNamespace(date=date(2027, 2, 28), asset_return=Decimal(".25"), locked=False))
    result = sell(fund, plan, date(2027, 12, 31))
    assert result["carry"] == Decimal(3600)
    assert result["proceeds"] == Decimal(94400)
