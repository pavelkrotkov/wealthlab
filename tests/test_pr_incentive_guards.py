"""Unresolved special-tax credits and inconsistent allocations withhold only affected views."""

from datetime import date
from decimal import Decimal

from wealthlab.tax.pr_incentive_examples import legacy_dividends, new_gain
from wealthlab.tax.pr_incentives import evaluate


def test_us_source_new_four_percent_credit_is_not_invented():
    # US dividends stay federally taxable. The new local special tax does not
    # establish whether a Code Schedule C credit offsets that special tax.
    comparison = legacy_dividends()
    annual = comparison.annual
    row = annual.income[0].model_copy(update={"received": date(2029, 12, 31)})
    baseline = annual.baseline.model_copy(
        update={
            "policy": annual.baseline.policy.model_copy(update={"year": 2029}),
            "nj_regime": "freeze_2025",
        }
    )
    annual = annual.model_copy(
        update={
            "income": [row],
            "baseline": baseline,
            "primary": annual.primary.model_copy(update={"local_end": date(2029, 12, 31)}),
            "pr_regime": "freeze_2025",
        }
    )
    decree = comparison.decree.model_copy(
        update={
            "application_date": date(2027, 1, 1),
            "granted_on": date(2027, 2, 1),
            "effective_from": date(2027, 1, 1),
            "six_prior_years_nonresident": "assumed",
            "valid_until": date(2055, 12, 31),
        }
    )
    result = evaluate(
        comparison.model_copy(
            update={"annual": annual, "decree": decree, "other_preferential_entitlement": "fails"}
        )
    )
    assert result["ordinary"] is not None
    assert result["incentive"] is None
    assert "4%/5%" in " ".join(result["qualification"]["reasons"])


def test_unconfirmed_other_favorable_treatment_does_not_assume_new_four_percent():
    comparison = new_gain().model_copy(update={"other_preferential_entitlement": "unset"})
    result = evaluate(comparison)
    assert result["ordinary"] is not None
    assert result["incentive"] is None


def test_duplicate_and_absent_gain_allocations_do_not_fabricate_sources():
    # A receipt has one dated basis/FMV history. Duplicate mappings must not
    # double the sale or invent a different source split for the same gain.
    comparison = new_gain()
    duplicate = comparison.model_copy(update={"gains": comparison.gains * 2})
    result = evaluate(duplicate)
    assert result["ordinary"] is None
    assert "only one" in result["reasons"][0]
    missing = evaluate(comparison.model_copy(update={"gains": []}))
    assert missing["incentive"] is None
    assert "Every capital gain" in missing["reasons"][0]


def test_preferential_deductions_and_prior_abt_history_remain_guarded():
    # A2 deductions use rounded source allocations; prior ABT is a separate
    # stock of credits. Neither can be substituted with a flat percentage.
    comparison = new_gain()
    annual = comparison.annual.model_copy(update={"pr_allowed_deductions": Decimal(10)})
    result = evaluate(
        comparison.model_copy(update={"annual": annual, "prior_abt_credit": Decimal(10)})
    )
    assert result["ordinary"] is None
    assert "deductions" in " ".join(result["reasons"])
    assert "ABT" in " ".join(result["reasons"])
