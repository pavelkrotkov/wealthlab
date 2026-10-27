"""Prepared policy keeps Pub570 proration and native FTC/AMT/NIIT/payroll order.

Half the worldwide wages are excluded under supplied PR residence facts, so
only half the standard deduction applies to the US-included 50,000. A plain
ordinary-policy evaluation would incorrectly use the full standard deduction.
"""

from decimal import Decimal

import pytest
from pr_execution_helpers import annual, credit_case

from wealthlab.tax.annual import evaluate
from wealthlab.tax.foreign_credit import evaluate as credit
from wealthlab.tax.foreign_credit_facts import ForeignCredits
from wealthlab.tax.pr_candidate import paid_us_tax
from wealthlab.tax.pr_execution_context import prepare
from wealthlab.tax.pr_federal import calculate
from wealthlab.tax.pr_local import calculate as local_tax
from wealthlab.tax.pr_recognition import recognized


def test_prepared_pr_exclusion_keeps_proportional_std_and_worldwide_employee_payroll():
    result = evaluate(annual())["federal"]
    assert (result["pr_excluded_income"], result["standard_deduction"]) == (50000, 7875)
    assert result["taxable_income"] == 42125
    assert result["income_tax"] == Decimal("4816.50")
    assert result["employee_payroll"] == 7650
    assert result["foreign_tax_credit"] == result["niit"] == 0


def test_native_prepared_credit_bypasses_legacy_subtraction_and_preserves_pr_paid_us_order_once():
    case, _ = prepare(annual(government=True))
    case = case.model_copy(
        update=dict(
            pr_income_tax_paid_for_us_credit=Decimal(2000),
            credit_evidence="Legacy claim deliberately present in test",
        )
    )
    facts = ForeignCredits(regular=1000, eligibility="allowed", source="Supplied permitted fact")
    result = calculate(case, case.income, case.income, native_credits=facts)
    assert result["foreign_tax_credit"] == 1000
    assert result["income_tax"] == 12449
    paid = paid_us_tax(result, case.income, recognized(case))
    assert paid == 12449
    local = local_tax(case, recognized(case), paid)
    assert local["regular_credit"]["reported_paid_or_accrued"] == paid
    assert "legacy subtraction bypassed" in result["foreign_credit"]["method"]


def test_excluded_pr_income_tax_preserves_actual_cash_but_cannot_generate_credit_or_carry():
    result = credit(credit_case())
    assert result["candidate"] is None
    assert result["observed_tax_cash_outflow_usd"] == 10000
    assert result["carry_audit"] is None
    assert any("PR-excluded" in reason for reason in result["unresolved"])


def test_government_service_exception_retains_included_pr_source_and_independently_limited_credit():
    result = credit(credit_case(government=True))
    assert result["candidate"] is not None
    assert result["candidate"]["federal"]["foreign_tax_credit"] == Decimal("6724.50")
    assert result["candidate"]["federal"]["employee_payroll"] == 7650
    assert result["basket_audit"][0]["gross"] == 50000


def test_oversized_prepared_credit_cannot_use_ordinary_worldwide_policy_tax_capacity():
    case = annual()
    facts = ForeignCredits(regular=5000, eligibility="allowed", source="Deliberately oversized")
    with pytest.raises(ValueError, match="actual pre-credit regular tax"):
        evaluate(case.model_copy(update=dict(foreign_credits=facts)))
