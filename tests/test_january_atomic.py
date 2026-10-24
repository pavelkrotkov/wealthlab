"""Rejected original-year tax recovery leaves all consumer records unchanged.

The coordinator uses an actual wash book and closed tax return, plus a real
Medicare ledger containing the provisional return. A smaller NJ liability
creates an itemized tax-benefit recovery that cannot be inferred. The failed
correction must not publish a revised lookback while retaining old taxes.
"""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest

from tests.return_reconciliation_cases import close_december
from tests.test_january_medicare import case as medicare_case
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_book import Ledger as Lots
from wealthlab.portfolio.household_recognition import totals
from wealthlab.portfolio.household_wash import bind, reconcile
from wealthlab.portfolio.january_example import synthetic
from wealthlab.retirement.medicare_household import Ledger as Medicare


def setup():
    taxes, _ = close_december(100000, itemized=True)
    medicare = Medicare(Scenario.model_validate(medicare_case()))
    position = taxes.closed_returns[2026]
    medicare.observe(SimpleNamespace(case=position.case, result=position.result), date(2027, 1, 1))
    data = synthetic().model_dump(mode="json")
    data["lot_plan"]["case"]["nj_wash_treatment"] = "federal_rules"
    lots = Lots(Scenario.model_validate(data))
    lots.book.trade(lots.case.trades[0])
    federal, _, _ = totals(lots.case, lots.book, date(2027, 1, 31))
    lots.reported[2026] = (dict.fromkeys(federal, Decimal(0)), Decimal(0))
    bind(lots, taxes, None, medicare, None)
    taxes.provisional_returns.add(2026)
    return lots


def test_rejected_return_revision_cannot_rewrite_the_medicare_lookback():
    lots = setup()
    prior = lots.medicare.case
    position = lots.taxes.closed_returns[2026]
    with pytest.raises(ValueError, match="state_refund_taxable_fractions"):
        reconcile(lots, 2026, date(2027, 1, 31))
    assert lots.medicare.case is prior
    assert lots.taxes.closed_returns[2026] is position
    assert lots.taxes.provisional_returns == {2026}
    assert lots.reconciliations == []
