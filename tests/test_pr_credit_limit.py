"""Paid-tax and source-income limits remain separate for regular and alternative taxes."""

from decimal import Decimal

from wealthlab.tax.pr_credit_limit import limited


def test_foreign_source_fraction_caps_each_tax_computation_independently():
    regular = limited(Decimal(12000), Decimal(5000), Decimal(20000), Decimal(80000))
    alternative = limited(Decimal(4000), Decimal(5000), Decimal(20000), Decimal(80000))
    assert regular["allowed"] == 3000
    assert alternative["allowed"] == 1000
    assert regular["unused_eligible"] == 2000


def test_exempt_foreign_income_reduces_paid_tax_before_applying_local_limit():
    result = limited(
        Decimal(12000),
        Decimal(5000),
        Decimal(20000),
        Decimal(80000),
        excluded_foreign_net=Decimal(30000),
        paid_net=Decimal(50000),
    )
    assert result["paid_tax_reduction"] == 3000
    assert result["eligible_paid_tax"] == result["allowed"] == 2000


def test_no_taxable_net_income_cannot_create_a_refund_or_credit():
    result = limited(Decimal(0), Decimal(5000), Decimal(0), Decimal(0))
    assert result["allowed"] == 0
