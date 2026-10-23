"""Cash receipt and qualification can cross years without moving the configured income year."""

from datetime import date

from distribution_cases import distribution_case
from test_dividend_qualification import recently_acquired

from wealthlab.portfolio.book import Book
from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run
from wealthlab.portfolio.tax_budget import impact
from wealthlab.portfolio.timeline import replay


def test_january_payment_can_have_explicit_prior_december_recognition():
    payload = distribution_case()
    payload["distributions"][0].update(
        ex_date="2026-12-15", payment_date="2027-01-15", recognition_date="2026-12-31"
    )
    december = run(LotCase.model_validate(payload))
    assert december["distribution_receivable"] == 100
    assert december["closing_cash"] == 1000
    assert december["annual_tax_comparison"][0]["distribution_federal"]["dividends"] == 100
    payload["end"] = "2027-01-31"
    annual = payload["lot_tax_cases"][0]
    payload["lot_tax_cases"].append(dict(annual, policy=dict(annual["policy"], year=2027)))
    january = run(LotCase.model_validate(payload))
    assert january["closing_cash"] == 1100
    assert january["distribution_receivable"] == 0
    assert not january["annual_tax_comparison"][1]["distribution_federal"]


def test_tax_budget_uses_observed_holding_days_not_the_projection_end():
    payload = recently_acquired()
    full = LotCase.model_validate(payload)
    book = Book(full)
    replay(full, book)
    current = impact(full, book, date(2026, 6, 20))
    early = run(full.model_copy(update={"end": date(2026, 6, 20)}))
    late = run(full)
    assert current == early["annual_tax_comparison"][0]["incremental_liability"]
    assert current > late["annual_tax_comparison"][0]["incremental_liability"]
