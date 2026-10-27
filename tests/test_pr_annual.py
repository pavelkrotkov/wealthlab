"""Independent annual arithmetic and unchanged raw-wage payroll across jurisdictions."""

from decimal import Decimal

import pytest

from wealthlab.tax.pr_annual import evaluate
from wealthlab.tax.pr_examples import synthetic
from wealthlab.tax.pr_facts import PRCase


def edit(case=None, **changes):
    data = (case or synthetic()).model_dump(mode="json")
    data.update(changes)
    return PRCase.model_validate(data)


def test_full_year_wages_matches_primary_schedule_and_keeps_payroll():
    # 96,500 net through regular brackets = 19,980; the <=100k reduction is 92%.
    # Section 933 excludes the PR-source wages, but not the original FICA base.
    result = evaluate(synthetic())
    candidate = result["candidate"]
    assert not result["reasons"]
    assert candidate["conditional"]
    assert candidate["federal"]["income_tax"] == 0
    assert candidate["excluded_federal"] == 100000
    assert candidate["puerto_rico"]["income_tax"] == Decimal("18381.60")
    assert candidate["employee_payroll"] == 7650


def test_mainland_comparator_preserves_independent_nj_and_matched_scope():
    # Compare only federal + PR + payroll against federal + payroll.
    # NJ remains visible independently because move-year state tax is not modeled.
    result = evaluate(synthetic())
    candidate = result["candidate"]
    assert candidate["federal_pr_payroll_total"] == Decimal("26031.60")
    assert candidate["federal_pr_difference"] == Decimal("4932.60")
    assert result["baseline"]["new_jersey"]["income_tax"] == 4182
    assert "issue 17" in result["limitation"]


def test_payments_never_change_candidate_liability():
    # A withholding remittance changes the balance due, never the tax calculation.
    base = synthetic().baseline.model_dump(mode="json")
    base["payments"]["federal_income_withheld"] = "99999"
    result = evaluate(edit(baseline=base))
    assert result["candidate"]["federal_pr_payroll_total"] == Decimal("26031.60")
    assert result["baseline"]["federal_income_balance"] == -86550


def test_unset_residence_keeps_mainland_runnable_and_withholds_benefit():
    result = evaluate(edit(primary={}))
    assert result["candidate"] is None
    assert result["baseline"]["total_liability"] > 0
    assert "unconfirmed" in " ".join(result["reasons"])


def test_government_wages_are_not_933_excluded():
    # The statutory US-government wage exception survives bona fide residence.
    rows = [synthetic().income[0].model_dump(mode="json")]
    rows[0]["us_government_wages"] = True
    result = evaluate(edit(income=rows))["candidate"]
    assert result["federal"]["income_tax"] == 13449
    assert result["excluded_federal"] == 0
    assert result["puerto_rico"]["regular_credit"]["allowed"] == 0


def test_non_bfr_us_source_wages_local_credit_uses_post_federal_tax():
    # Same worldwide wages: US tax 13,449 credits against PR regular 18,381.60.
    # Credit reduces PR liability to 4,932.60, without touching employee payroll.
    case = synthetic()
    residence = case.primary.model_dump(mode="json")
    residence["federal_bfr"] = "no"
    rows = [case.income[0].model_dump(mode="json")]
    rows[0].update(federal_source="US", pr_source="US")
    result = evaluate(edit(primary=residence, income=rows))["candidate"]
    assert result["puerto_rico"]["regular_credit"]["allowed"] == 13449
    assert result["puerto_rico"]["income_tax"] == Decimal("4932.60")
    assert result["federal_pr_payroll_total"] == Decimal("26031.60")


@pytest.mark.parametrize(
    "field,value", [("pr_regime", "published_2025"), ("pr_allowed_deductions", "100001")]
)
def test_explicit_profile_boundaries(field, value):
    data = synthetic().model_dump(mode="json")
    if field == "pr_regime":
        data["baseline"]["policy"]["year"] = 2026
        data["baseline"]["nj_regime"] = "freeze_2025"
        data["income"][0]["received"] = "2026-12-31"
    data[field] = value
    result = evaluate(PRCase.model_validate(data))
    assert result["candidate"] is None
    assert result["reasons"]


def test_source_rows_must_reconcile_and_be_dated_in_year():
    data = synthetic().model_dump(mode="json")
    data["income"][0]["federal_amount"] = "99999"
    with pytest.raises(ValueError, match="reconcile"):
        evaluate(PRCase.model_validate(data))
    data["income"][0]["received"] = "2024-12-31"
    with pytest.raises(ValueError, match="tax year"):
        evaluate(PRCase.model_validate(data))
