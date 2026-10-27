"""Regional relief remains separate from actual IP payments and solidarity credit."""

from decimal import Decimal

import pytest
from spain_regional_cases import case

from wealthlab.tax.spain import evaluate
from wealthlab.tax.spain_inputs import SpainCase


@pytest.mark.parametrize("region", ["andalusia", "murcia", "la_rioja", "cantabria"])
def test_replacement_bonus_preserves_solidarity_sized_ip_and_does_not_pay_it(region):
    result = evaluate(SpainCase.model_validate(case(region)))["wealth"]["assessment"]
    assert result["wealth_liability"] == Decimal("5100")
    assert result["solidarity_liability"] == Decimal("5100")
    assert result["wealth_actually_paid"] == 0


def test_extremadura_full_minor_quota_bonus_does_not_reduce_solidarity():
    result = evaluate(SpainCase.model_validate(case("extremadura")))["wealth"]["assessment"]
    assert result["wealth_liability"] == 0
    assert result["regional_bonus"] == result["wealth"]["capped_quota"]
    assert result["solidarity_liability"] == Decimal("5100")


def test_cantabria_low_wealth_bonus_is_full():
    result = evaluate(SpainCase.model_validate(case("cantabria", "3000000")))
    assert result["wealth"]["assessment"]["wealth_liability"] == 0
