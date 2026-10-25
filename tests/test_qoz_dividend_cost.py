"""Declared E&P dividends do not inherit the final stock-interest selling-cost rate.

A $100,000 interest pays a $10,000 ordinary cash dividend, leaving $90,000 NAV.
A later full sale with the independently supplied 2% selling cost pays $88,200.
Total cash is $98,200, conserving opening capital less only the $1,800 sale cost.
"""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest
from qoz_cases import flat

from wealthlab.household.projection import project
from wealthlab.products.long_short_book import equity
from wealthlab.products.qoz_economics import create, distribute, sell


def test_cash_dividend_has_no_stock_sale_fee_and_final_sale_still_pays_its_own_cost():
    plan = flat().qoz_plan
    case = plan.economics.model_copy(update=dict(exit_cost=Decimal(".02")))
    plan = plan.model_copy(update=dict(economics=case))
    tranche = create(plan, Decimal(100000), date(2027, 1, 31))
    dividend = distribute(
        tranche, SimpleNamespace(dividend_fraction_of_nav=Decimal(".10"), locked=False)
    )
    assert dividend == Decimal(10000)
    assert equity(tranche["book"]) == Decimal(90000)
    result = sell(tranche, plan, date(2027, 12, 31))
    assert result["liquidation_cost"] == Decimal(1800)
    assert dividend + result["proceeds"] == Decimal(98200)


def test_partial_call_contract_cannot_be_assumed_when_its_terms_are_unconfirmed():
    scenario = flat()
    plan = scenario.qoz_plan.model_copy(
        update=dict(calls_are_optional_partial_subscriptions_assumed_confirmed=False)
    )
    with pytest.raises(ValueError, match="Confirm independent"):
        project(scenario.model_copy(update=dict(qoz_plan=plan)))
