"""Independent application-date, statutory sunset and strict elapsed-year boundaries."""

from datetime import date

from wealthlab.tax.pr_decree import pre_rate, qualification, rate
from wealthlab.tax.pr_incentive_examples import legacy_dividends


def test_application_cutover_is_not_grant_date():
    decree = legacy_dividends().decree
    legacy = decree.model_copy(
        update={
            "application_date": date(2026, 12, 31),
            "granted_on": date(2027, 2, 1),
            "effective_from": date(2027, 1, 1),
        }
    )
    new = legacy.model_copy(update={"application_date": date(2027, 1, 1)})
    assert rate(legacy, date(2028, 1, 1)) == 0
    assert rate(new, date(2028, 1, 1)) == 4
    assert rate(legacy, date(2036, 1, 1)) is None


def test_new_regime_needs_both_historical_eligibility_claims():
    comparison = legacy_dividends()
    decree = comparison.decree.model_copy(
        update={"application_date": date(2027, 1, 1), "granted_on": date(2027, 2, 1)}
    )
    assert not qualification(decree, comparison.annual)["eligible"]
    decree = decree.model_copy(update={"six_prior_years_nonresident": "assumed"})
    assert qualification(decree, comparison.annual)["eligible"]
    decree = decree.model_copy(update={"nonresident_during_2006_2012_window": "unset"})
    assert not qualification(decree, comparison.annual)["eligible"]


def test_local_five_percent_uses_elapsed_years_and_program_sunset():
    # The federal prior-tax-year source history is a separate fact. Local five
    # percent requires recognition after ten elapsed years and before sunset.
    decree = legacy_dividends().decree
    resident = date(2015, 1, 1)
    assert pre_rate(decree, date(2025, 1, 1), resident) == 15
    assert pre_rate(decree, date(2025, 1, 2), resident) == 5
    assert pre_rate(decree, date(2036, 1, 1), resident) == 15


def test_unconfirmed_application_does_not_become_a_granted_compliant_decree():
    comparison = legacy_dividends()
    assert not qualification(
        comparison.decree.model_copy(update={"status": "denied"}), comparison.annual
    )["eligible"]
    assert not qualification(
        comparison.decree.model_copy(update={"granted_on": None}), comparison.annual
    )["eligible"]
    assert not qualification(
        comparison.decree.model_copy(update={"compliance": "fails"}), comparison.annual
    )["eligible"]
