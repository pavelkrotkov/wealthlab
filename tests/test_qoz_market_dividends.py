"""Declared ordinary dividends create actual cash once; factor returns do not manufacture yield."""

from decimal import Decimal

from tests.qoz_market_cases import flat
from wealthlab.markets.household_run import run


def test_native_declared_dividend_reduces_nav_and_changes_actual_tax_character():
    case, batch, binding = flat()
    observations = list(case.qoz_plan.observations)
    observations[2] = observations[2].model_copy(
        update=dict(dividend_fraction_of_nav=Decimal(".1"))
    )
    plan = case.qoz_plan.model_copy(update=dict(observations=observations))
    rows = run(case.model_copy(update=dict(qoz_plan=plan)), batch, binding)["details"][0]["rows"]
    # The same $80k capital returns as $8k ordinary E&P dividend +$72k stock proceeds.
    # Ex-dividend inclusion is $72k; $8k ordinary income replaces that capital character.
    assert rows[2]["qoz_dividends"] == 8000
    assert rows[2]["qoz_nav"] == 72000
    assert rows[-1]["qoz_original_gain_included"] == rows[-1]["qoz_settlement_cash"] == 72000
    assert rows[-1]["annual_tax"]["total_liability"] == 19381
    assert rows[-1]["closing_cash"] == rows[-1]["net_wealth"] == 157619
