"""Independent cent/dollar examples keep SMI before rounding and Part D afterwards.

Part D uses a single combined payment per recipient and is never collected
partially. A small active Part B record stays outside this profile instead of
producing a negative check or assuming an unverified collection from another
record. Positive benefits without SMI still retain their sub-dollar amount.
"""

from decimal import Decimal

import pytest

from wealthlab.retirement.social_amounts import dollar
from wealthlab.retirement.social_medicare_math import calculate


def row(own="2500.70", spouse="0"):
    return dict(
        own_with_delayed_credits=Decimal(own),
        spousal_excess=Decimal(spouse),
        survivor_excess=Decimal(0),
        issued_before_offsets=dollar(Decimal(own)) + dollar(Decimal(spouse)),
    )


def test_part_b_rounding_precedes_part_d_and_tax_gross_adds_premiums_back():
    result = calculate(
        row(), dict(part_b=Decimal("202.90"), d_irmaa=Decimal("14.50")), "own_with_delayed_credits"
    )
    assert result["gross_credited"] == Decimal("2499.90")
    assert result["cash_received"] == Decimal("2282.50")
    assert result["part_b_withheld"] + result["part_d_irmaa_withheld"] == Decimal("217.40")
    assert result["change_from_no_premium_rounding"] == Decimal("-.10")


def test_each_dual_record_keeps_its_own_rounding():
    result = calculate(
        row("1240.90", "161.70"),
        dict(part_b=Decimal("202.90"), d_irmaa=0),
        "own_with_delayed_credits",
    )
    assert result["gross_credited"] == Decimal("1401.90")
    assert result["cash_received"] == 1199
    assert result["credited_records"]["spousal_excess"] == 161


def test_part_d_is_billed_entirely_if_single_record_has_insufficient_cash():
    result = calculate(
        row("210"),
        dict(part_b=Decimal("202.90"), d_irmaa=Decimal("14.50")),
        "own_with_delayed_credits",
    )
    assert result["cash_received"] == 7
    assert result["part_d_irmaa_withheld"] == 0
    assert result["part_d_irmaa_direct_bill"] == Decimal("14.50")


@pytest.mark.parametrize("own", ["0.50", "200", "203.50"])
def test_low_benefit_smi_exceptions_are_explicitly_outside_current_profile(own):
    with pytest.raises(ValueError, match="sufficient active benefit"):
        calculate(row(own), dict(part_b=Decimal("202.90"), d_irmaa=0), "own_with_delayed_credits")


@pytest.mark.parametrize("spouse,net,held", [("10", "2.50", "14.50"), ("5", "12", "0")])
def test_part_d_uses_the_combined_payment_and_is_never_partially_withheld(spouse, net, held):
    result = calculate(
        row("210", spouse),
        dict(part_b=Decimal("202.90"), d_irmaa=Decimal("14.50")),
        "own_with_delayed_credits",
    )
    assert result["cash_received"] == Decimal(net)
    assert result["part_d_irmaa_withheld"] == Decimal(held)


def test_without_smi_a_positive_sub_dollar_benefit_remains_payable():
    result = calculate(row("0.50"), None, "own_with_delayed_credits")
    assert result["cash_received"] == result["gross_credited"] == Decimal("0.50")
    assert result["change_from_no_premium_rounding"] == 0


def test_premium_part_a_needs_its_own_collection_profile():
    with pytest.raises(ValueError, match="Premium Part A"):
        calculate(
            row(), dict(part_a=311, part_b=Decimal("202.90"), d_irmaa=0), "own_with_delayed_credits"
        )
