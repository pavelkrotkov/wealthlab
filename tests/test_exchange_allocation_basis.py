"""Zero, partial and full choices split actual shares and independent bases."""

import pytest
from exchange_allocation_cases import allocated

from wealthlab.products.exchange_fund_household import Ledger


@pytest.mark.parametrize("quantity", [0, 400, 1000])
def test_requested_allocation_reconciles_exact_original_units_and_independent_bases(quantity):
    ledger = Ledger(allocated(quantity))
    source = list(ledger.book.lots.values())
    assert sum(lot.quantity for lot in source) == 1000 - quantity
    assert sum(lot.federal_basis for lot in source) == 20000 - quantity * 20
    assert sum(lot.nj_basis for lot in source) == 30000 - quantity * 30
    assert ledger.bases == dict(federal=quantity * 20, nj=quantity * 30)
    assert ledger.nav + sum(lot.quantity * 100 for lot in source) == 100000


def test_zero_contribution_has_no_fund_or_opening_tax_event():
    ledger = Ledger(allocated(0))
    assert ledger.active is False
    assert ledger.opening_events == []
    assert ledger.pending == []
    assert ledger.book.lots["original_lot"].acquired == ledger.plan.source_lot.acquired
