"""Later path returns do not reprice an earlier invoice on stored opening equity."""

from decimal import Decimal

import pytest

from tests.advisory_cases import native
from tests.advisory_snapshot_cases import snapshot_fee
from wealthlab.markets.household_run import run


@pytest.mark.parametrize("future_shock, ending", [(0, "114747.22"), (0.5, "169747.22")])
def test_advance_bill_never_uses_current_or_future_quotes_instead_of_selected_opening(
    future_shock, ending
):
    shocks = [
        dict(name="January growth", month=0, mark_shocks=dict(source_stock=0.1)),
        dict(name="future April", month=3, mark_shocks=dict(source_stock=future_shock)),
    ]
    case, batch, binding = native(shocks=shocks)
    case = snapshot_fee(
        case, billed="2026-03-31", start="2026-04-01", end="2026-07-01", advance=True
    )
    rows = run(case, batch, binding)["details"][0]["rows"]
    assert rows[2]["advisory_fee_assessments"][0]["valuation_base"] == 100000
    assert rows[2]["account_balances"]["brokerage"] == 110000
    assert rows[2]["advisory_fees_paid"] == Decimal("252.78")
    assert rows[-1]["net_wealth"] == Decimal(ending)
