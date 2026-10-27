"""Canonical revised returns supersede liability without changing historical cash.

The native fixture invests $80,000 from the actual prior-year stock sale.
Its source-year tax is then zero, but the already paid cash returns only at
the scheduled refund date. Combined wealth stays $105,000. Separate historical
audit lists cannot override the final closed return or clear an unresolved
wash window merely because another product amended the same source year.
"""

from copy import deepcopy

import pytest
from qoz_transition_cases import transition

from wealthlab.household.projection import project
from wealthlab.tax.household_reporting import annual_results, provisional_years, revisions, summary


@pytest.fixture(scope="module")
def rows():
    return project(transition())


def test_actual_qoz_revision_reconciles_generic_tax_summary_without_rewriting_payments(rows):
    paid = rows[11]["tax_settlement_paid"]
    report = summary(rows)
    assert paid > 0
    assert rows[11]["annual_tax"]["total_liability"] == paid
    assert annual_results(rows)["2026"]["total_liability"] == 0
    assert report["reported_tax_liability"] == report["net_cash_taxes_paid"] == 0
    assert report["gross_cash_taxes_paid"] == report["cash_tax_refunds_received"] == paid
    assert rows[-1]["net_wealth"] == 105000
    assert revisions(rows) == rows[-1]["qoz_audit"]["source_return_revisions"]


def test_old_or_incomplete_qoz_result_requires_reexecution_instead_of_stale_liability(rows):
    observed = deepcopy(rows)
    del observed[-1]["qoz_audit"]["final_source_returns"]
    with pytest.raises(ValueError, match="rerun the projection"):
        annual_results(observed)


def test_a_qoz_revision_cannot_clear_an_unresolved_wash_return():
    observed = [
        dict(date="2026-12-01", tax_return_provisional=True),
        dict(
            date="2027-01-01",
            tax_return_provisional=False,
            qoz_audit=dict(source_return_revisions=[dict(year=2026)]),
        ),
    ]
    assert provisional_years(observed) == ["2026"]
