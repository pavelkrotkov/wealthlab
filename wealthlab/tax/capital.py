"""Schedule D character-preserving carryover, including unused low-income losses."""

from decimal import Decimal


def next_carry(
    short_term: Decimal, long_term: Decimal, taxable_before_zero: Decimal, deducted_loss: Decimal
) -> dict[str, Decimal]:
    """Apply the IRS capital-loss carryover worksheet using signed Schedule D nets.

    `taxable_before_zero` is Form 1040 taxable income before flooring at zero.
    The ordinary loss deduction consumes carry only to the extent permitted by
    worksheet lines 1-4; low-income households can retain the unused deduction.
    """
    usable = min(deducted_loss, max(Decimal(0), taxable_before_zero + deducted_loss))
    short_loss = max(Decimal(0), -short_term)
    long_loss = max(Decimal(0), -long_term)
    short_next = max(Decimal(0), short_loss - usable - max(Decimal(0), long_term))
    long_used = max(Decimal(0), usable - short_loss) + max(Decimal(0), short_term)
    return dict(short_term=short_next, long_term=max(Decimal(0), long_loss - long_used))
