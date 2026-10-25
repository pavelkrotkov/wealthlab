"""Conserve capital through existing leveraged accounting and the new actual carry charge."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from qoz_cases import flat

from wealthlab.products.qoz_economics import create, distribute, sell, step

D = Decimal


def test_actual_fee_financing_dividend_and_carry_have_an_independent_cash_identity():
    plan = flat().qoz_plan
    case = plan.economics.model_copy(
        update=dict(long_multiple=D(2), annual_financing_rate=D(".12"), annual_manager_fee=D(".12"))
    )
    plan = plan.model_copy(update=dict(economics=case, carry_fraction=D(".20")))
    tranche = create(plan, D(100000), date(2027, 1, 31))
    observation = SimpleNamespace(
        date=date(2027, 2, 28),
        asset_return=D(".10"),
        dividend_fraction_of_nav=D(".10"),
        locked=False,
    )
    row = step(tranche, observation)
    assert (row["long_price_pnl"], row["financing_cost"], row["manager_fee"]) == (
        D(20000),
        D(1000),
        D(1000),
    )
    dividend = distribute(tranche, observation)
    assert dividend == D(11800)
    sale = sell(tranche, plan, observation.date)
    assert sale["carry"] == D(3600)
    assert dividend + sale["proceeds"] == D(100000) + D(20000) - D(2000) - D(3600)


def test_a_preferred_hurdle_is_not_a_payment_or_a_guaranteed_yield():
    plan = flat().qoz_plan.model_copy(
        update=dict(preferred_hurdle=D(".08"), carry_fraction=D(".20"))
    )
    tranche = create(plan, D(100000), date(2027, 1, 31))
    observation = SimpleNamespace(
        date=date(2027, 2, 28), asset_return=D("-.20"), dividend_fraction_of_nav=D(0), locked=False
    )
    step(tranche, observation)
    sale = sell(tranche, plan, observation.date)
    assert sale["carry"] == 0
    assert sale["proceeds"] == D(80000)
