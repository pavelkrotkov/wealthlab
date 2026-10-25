"""Independent Black-Scholes and put-call parity cover QuantLib wiring and model scope."""

from decimal import Decimal
from math import erf, exp, sqrt

import pytest

from tests.option_cases import one_leg, parse
from wealthlab.products.option_engine import run
from wealthlab.products.option_stress import stress
from wealthlab.products.option_valuation import value


def test_quantlib_matches_independent_one_year_european_call_and_put_parity():
    case = parse(one_leg())
    mark, leg = case.marks[0], case.legs[0]
    normal = lambda x: (1 + erf(x / sqrt(2))) / 2  # noqa: E731
    expected = 100 * normal(0.3) - 100 * exp(-0.04) * normal(0.1)
    call = value(leg, mark)
    put = value(leg.model_copy(update=dict(kind="put")), mark)
    assert float(call) == pytest.approx(expected, abs=1e-9)
    assert float(call - put) == pytest.approx(100 - 100 * exp(-0.04), abs=1e-9)


def test_american_put_model_has_at_least_immediate_exercise_value():
    case = parse(one_leg("put"))
    leg = case.legs[0].model_copy(update=dict(style="american"))
    mark = case.marks[0].model_copy(update=dict(stock=Decimal(30)))
    assert value(leg, mark) >= 70


def test_stress_revalues_both_axes_instead_of_extrapolating_stock_protection():
    from wealthlab.products.option_example import synthetic

    result = stress(synthetic())
    assert len(result) == 9
    same_stock = [row for row in result if row["stock_shock"] == -0.4]
    assert len({row["option_value"] for row in same_stock}) == 3
    assert all(len(row["legs"]) == 4 for row in result)


def test_explicit_early_close_uses_execution_quote_while_unwind_uses_model_mark():
    data = one_leg()
    data["events"] = [dict(leg_id="contract", date="2025-06-01", action="close", close_price="7")]
    result = run(parse(data))
    assert result["terminations"][0]["pnl"] == 200
    assert result["ending"]["cash"] == 10200
    assert result["assumptions"]["marks"][0]["source"].startswith("Invented")
