"""Independent actual-day, signed cash and ambiguous-root return checks."""

from datetime import date
from decimal import Decimal

import pytest

from tests.test_life_illustration_cash import point, study
from wealthlab.products.dated_irr import calculate
from wealthlab.products.life_illustration_inputs import LifeStudy


def test_actual_dates_use_actual_365_and_aggregate_same_date_cash():
    row = calculate([(date(2028, 1, 1), Decimal(-1000)), (date(2029, 1, 1), Decimal(1100))])
    assert row["rate"] == pytest.approx(1.1 ** (365 / 366) - 1)
    net = calculate(
        [
            (date(2026, 1, 1), Decimal(-1000)),
            (date(2026, 1, 1), Decimal(-100)),
            (date(2027, 1, 1), Decimal(1100)),
        ]
    )
    assert net["rate"] == pytest.approx(0, abs=1e-9)


@pytest.mark.parametrize("amount,expected", [("800", -0.2), ("1000", 0)])
def test_losses_and_zero_return_are_not_missing_values(amount, expected):
    data = study().model_dump(mode="json")
    data["illustrations"][0]["values"][0]["gross_surrender_value"] = amount
    assert point(LifeStudy.model_validate(data))["surrender_irr"]["rate"] == pytest.approx(
        expected, abs=1e-9
    )


@pytest.mark.parametrize("amounts", [[], [1000], [-1000], [-100, 230, -132], [100, -50, 100]])
def test_nonconventional_cashflows_never_choose_a_root(amounts):
    result = calculate(
        [(date(2026 + i, 1, 1), Decimal(amount)) for i, amount in enumerate(amounts)]
    )
    assert result["rate"] is None
