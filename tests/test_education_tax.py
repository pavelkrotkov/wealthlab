"""Only distributed earnings are federal income; conditional exceptions do not erase that income."""

from decimal import Decimal

import pytest

from tests.test_education_cash import calculate, payload
from wealthlab.retirement.education import run
from wealthlab.retirement.education_example import synthetic


def test_synthetic_tax_keeps_principal_and_recipients_separate():
    result = run(synthetic())
    parent, student = result["annual_tax_groups"]
    assert (parent["recipient"], student["recipient"]) == ("parent", "student")
    assert parent["federal_taxable_earnings"] == Decimal("1536.80")
    assert student["federal_taxable_earnings"] == Decimal("922.08")
    assert parent["federal_additional_tax"] == Decimal("153.68")
    assert student["federal_additional_tax"] == Decimal("92.21")


def test_conditional_exception_removes_only_additional_tax():
    data = payload()
    data["allocations"][0]["additional_tax_exempt_earnings"] = "1536.80"
    parent = calculate(data)["annual_tax_groups"][0]
    assert parent["federal_additional_tax"] == 0
    assert parent["federal_taxable_earnings"] == Decimal("1536.80")
    data["allocations"][0]["additional_tax_exempt_earnings"] = 2000
    with pytest.raises(ValueError, match="exceeds actual taxable earnings"):
        calculate(data)
