"""Return revisions change reported tax while actual cash retains its payment/refund dates."""

from wealthlab.household.example import synthetic as household
from wealthlab.household.projection import project
from wealthlab.portfolio.january_example import synthetic
from wealthlab.tax.household_reporting import annual_results, summary
from wealthlab.tax.projection_example import template


def test_january_revision_is_reported_without_rewriting_december_cash_payments():
    rows = project(synthetic())
    report = summary(rows)
    assert annual_results(rows)["2026"]["federal"]["agi"] == 59600
    assert rows[11]["annual_tax"]["federal"]["agi"] == 60000
    assert report["cash_tax_refunds_received"] == 48
    assert report["gross_cash_taxes_paid"] - report["reported_tax_liability"] == 48
    assert report["net_cash_taxes_paid"] == report["reported_tax_liability"]
    assert report["provisional_tax_years"] == report["partial_tax_years"] == []


def test_partial_year_is_accrued_recognition_and_is_explicitly_identified():
    from datetime import date

    scenario = household().model_copy(update=dict(end=date(2026, 7, 1)))
    scenario = scenario.model_copy(update=dict(tax_plan=template(scenario)))
    rows = project(scenario)
    report = summary(rows)
    assert report["partial_tax_years"] == ["2026"]
    assert report["reported_tax_liability"] == rows[-1]["annual_tax"]["total_liability"]
    assert report["provisional_tax_years"] == []
