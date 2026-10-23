"""Independent NJ schedule and category boundaries for the limited reuse spike."""

import pytest

from wealthlab.checks.new_jersey import category_income, joint_schedule


def test_category_netting():
    assert category_income(200_000, [50_000, -30_000]) == 220_000
    assert category_income(200_000, [-30_000]) == 200_000


def test_schedule_and_scope():
    assert joint_schedule(200_000) == pytest.approx(8_697.50)
    with pytest.raises(ValueError, match="only taxable"):
        joint_schedule(99_999)
