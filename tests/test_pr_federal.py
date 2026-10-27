"""Section 933 deduction allocation and explicit paid-tax limitation checks."""

from decimal import Decimal

import pytest

from wealthlab.tax.pr_annual import evaluate
from wealthlab.tax.pr_examples import synthetic
from wealthlab.tax.pr_facts import PRCase
from wealthlab.tax.pr_inputs import income


def split_case():
    data = synthetic().model_dump(mode="json")
    pr = data["income"][0]
    pr.update(federal_amount="20000", pr_amount="20000")
    us = dict(
        pr,
        kind="interest",
        federal_amount="8000",
        pr_amount="8000",
        federal_source="US",
        pr_source="US",
    )
    data["income"] = [pr, us]
    case = PRCase.model_validate(data)
    return case.model_copy(
        update={
            "baseline": case.baseline.model_copy(update={"federal_income": income(case.income)})
        }
    )


def test_pub570_ratio_allocates_standard_deduction_without_mutating_shared_engine():
    # Pub 570's 8,000 taxable / 28,000 worldwide example gives a 4,500 standard
    # deduction. Remaining ordinary income 3,500 is entirely in the 10% bracket.
    case = split_case()
    result = evaluate(case)["candidate"]["federal"]
    assert result["standard_deduction"] == 4500
    assert result["taxable_income"] == 3500
    assert result["income_tax"] == 350
    assert result["standard_ratio"] == Decimal(8000) / 28000
    assert evaluate(synthetic())["baseline"]["federal"]["standard_deduction"] == 15750


def test_ordinary_us_foreign_credit_never_offsets_payroll():
    # Without section 933 all wages are federally taxable. A general-category
    # credit is capped by income tax; neither payroll nor NIIT is its tax base.
    data = synthetic().model_dump(mode="json")
    data["primary"]["federal_bfr"] = "no"
    data.update(
        pr_income_tax_paid_for_us_credit="18381.60",
        credit_evidence="Synthetic paid PR ordinary tax, no excluded income",
    )
    candidate = evaluate(PRCase.model_validate(data))["candidate"]
    assert candidate["federal"]["foreign_credit"]["allowed"] == 13449
    assert candidate["federal"]["income_tax"] == 0
    assert candidate["employee_payroll"] == 7650


def test_preferential_us_credit_is_guarded_instead_of_using_ordinary_limit():
    # Form 1116 has preferential-income adjustments and separate baskets.
    # The ordinary-only limiter must not silently stand in for that worksheet.
    case = split_case()
    rows = [row.model_copy(update={"kind": "dividends"}) for row in case.income]
    baseline = case.baseline.model_copy(update={"federal_income": income(rows)})
    changed = case.model_copy(
        update={
            "income": rows,
            "baseline": baseline,
            "pr_income_tax_paid_for_us_credit": Decimal(100),
            "credit_evidence": "Synthetic",
        }
    )
    result = evaluate(changed)
    assert result["candidate"] is None
    assert "preferential" in result["reasons"][0]


@pytest.mark.parametrize(
    "change,reason",
    [
        ({"federal_source": "unset"}, "source classifications"),
        ({"kind": "long_term"}, "Capital gains"),
    ],
)
def test_unconfirmed_sources_and_gain_profiles_withhold_candidate(change, reason):
    case = synthetic()
    rows = [case.income[0].model_copy(update=change)]
    case = case.model_copy(
        update={
            "income": rows,
            "baseline": case.baseline.model_copy(update={"federal_income": income(rows)}),
        }
    )
    assert reason in " ".join(evaluate(case)["reasons"])
