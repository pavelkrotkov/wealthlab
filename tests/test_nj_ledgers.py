"""Independent NJ table and business-category examples, including expiry boundaries."""

from decimal import Decimal

import pytest

from wealthlab.tax.nj_business import BusinessIncome, BusinessLoss, adjustment
from wealthlab.tax.nj_rates import tax


@pytest.mark.parametrize(
    ("income", "status", "expected"),
    [
        (39875, "joint", "628"),
        (70000, "joint", "1296"),
        (70100, "joint", "1299"),
        (99999, "single", "4242"),
        (200000, "joint", "8697.50"),
        (100000, "single", "4243.75"),
        (1000001, "head", "72657.61"),
    ],
)
def test_published_tax_table(income, status, expected):
    assert tax(Decimal(income), status) == Decimal(expected)


def test_business_loss_does_not_deduct_all_losses_from_wages():
    """$40k partnership profit and $60k rent loss: $20k adjustment, $20k carry.

    Regular reportable business income remains $40k; half the difference
    from zero alternative income is deductible under NJ-BUS-2, not $60k.
    """
    result = adjustment(BusinessIncome(partnership=Decimal(40000), rents=Decimal(-60000)), 2025)
    assert result["regular_income"] == 40000
    assert result["adjustment"] == 20000
    assert result["carry"] == [BusinessLoss(year=2025, amount=Decimal(20000))]


def test_carry_consumption_and_twentieth_year_boundary():
    income = BusinessIncome(
        partnership=Decimal(6000),
        carry=[
            BusinessLoss(year=2012, amount=Decimal(5000)),
            BusinessLoss(year=2013, amount=Decimal(9000)),
        ],
    )
    result = adjustment(income, 2032)
    assert result["adjustment"] == 3000
    assert result["carry"] == [BusinessLoss(year=2013, amount=Decimal(8000))]
    expired = adjustment(income, 2033)
    assert expired["expired"] == 5000
    assert expired["carry"] == [BusinessLoss(year=2013, amount=Decimal(3000))]


def test_invalid_carry_and_tax_inputs_are_rejected():
    with pytest.raises(ValueError, match="before"):
        adjustment(BusinessIncome(carry=[BusinessLoss(year=2025, amount=Decimal(1))]), 2025)
    with pytest.raises(ValueError, match="nonnegative"):
        tax(Decimal(-1), "joint")
