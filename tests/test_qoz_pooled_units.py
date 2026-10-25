"""NAV-priced lots participate in the same later return and conserve every allocated cent."""

from decimal import Decimal

from qoz_pooled_cases import rising

from wealthlab.household.projection import project
from wealthlab.products.qoz_units import allocate


def test_different_subscription_dates_share_one_leveraged_company_return():
    rows = project(rising())
    assert rows[2]["qoz_nav"] == Decimal(144000)
    assert rows[2]["qoz_internal_debt"] == Decimal(120000)
    assert rows[2]["net_wealth"] == Decimal(149000)
    values = rows[-1]["qoz_audit"]["stock_values"][2]["values"]
    assert values == dict(call_one=Decimal(84000), second=Decimal(60000))


def test_tiny_nav_and_many_stock_lots_never_lose_or_create_a_cent():
    tranches = [dict(units=Decimal(1)) for _ in range(7)]
    amounts = allocate(Decimal(".04"), tranches)
    assert sum(amounts) == Decimal(".04")
    assert min(amounts) == 0
    assert max(amounts) == Decimal(".01")
