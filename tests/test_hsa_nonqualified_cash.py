"""Unfunded requests do not create income/tax or a second cash receipt."""

from hsa_distribution_cases import flat

from wealthlab.household.projection import project


def test_only_actual_funded_cash_generates_nonqualified_income_and_additional_tax():
    rows = project(flat(balance=3000, requested=5000, nj_fraction="0.5"))
    final = rows[-1]
    assert sum(r["hsa_withdrawal_cash"] for r in rows) == 3000
    assert (
        sum(r["hsa_nonqualified_taxable"] for r in rows),
        sum(r["hsa_additional_tax"] for r in rows),
        sum(r["hsa_nj_withdrawal_income"] for r in rows),
    ) == (3000, 600, 1500)
    assert sum(r["hsa_unfilled_requests"] for r in rows) == 2000
    assert final["closing_cash"] == final["net_wealth"] == 102400
    assert (final["annual_tax"]["federal"]["agi"], final["annual_tax"]["total_liability"]) == (
        3000,
        600,
    )
    assert sum(r["tax_event_cash"] for r in rows) == 0


def test_nonqualified_request_with_no_assets_is_unfilled_without_tax():
    rows = project(flat(balance=0, requested=5000))
    final = rows[-1]
    assert final["annual_tax"]["total_liability"] == 0
    assert sum(r["hsa_unfilled_requests"] for r in rows) == 5000
    assert final["net_wealth"] == 100000
