"""A real home close feeds actual net cash to the common fee book before optional saving."""

from calendar import monthrange
from decimal import Decimal as D

from wealthlab.household.advisory_example import plan
from wealthlab.household.calendar import money
from wealthlab.household.projection import project
from wealthlab.household.property_example import synthetic


def test_outer_cash_fees_observe_actual_net_proceeds_without_billing_uncovered_property():
    case = synthetic()
    case = case.model_copy(update=dict(advisory_fee_plan=plan(case)))
    rows = project(case)
    cash, assessed = D(20000), D(0)
    for month in range(1, 13):
        if month == 6:
            cash += 229400
        annual = min(cash, D(100000)) * D(".01") + max(D(0), cash - 100000) * D(".005")
        charge = money(annual * monthrange(2026, month)[1] / D(365))
        assessed += charge
        cash -= charge
        if month < 6:
            cash -= 600
    assert sum(r["advisory_fees_paid"] for r in rows) == assessed
    assert rows[-1]["net_wealth"] == cash
    assert (rows[5]["property_cash_received"], rows[5]["debt_payment"]) == (229400, 0)
    assert rows[-1]["advisory_fees_owed"] == 0
