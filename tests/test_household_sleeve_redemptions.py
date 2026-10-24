"""Actual redemptions fund spending once; optional unfilled requests are not extra bills."""

import pytest
from household_sleeve_cases import change, flat

from wealthlab.household.projection import project


@pytest.mark.parametrize("locked", [False, True])
def test_locked_capital_cannot_fund_spending_and_unfilled_request_is_not_double_counted(locked):
    def configure(data):
        sleeve = data["sleeve_plan"]["sleeves"][0]
        sleeve["case"]["redemptions"] = [
            dict(id="draw", provenance="assumption", date="2026-01-31", amount=20000)
        ]
        sleeve["observations"][0]["locked"] = locked
        data["expenses"] = [
            dict(
                id="living",
                provenance="assumption",
                start="2026-01-01",
                end="2026-02-01",
                monthly_amount=20000,
                currency="USD",
                annual_growth=0,
                category="essential",
            )
        ]

    row = project(change(flat(0), configure))[0]
    assert row["sleeve_redemptions"] == (0 if locked else 20000)
    assert row["funding_shortfall"] == (20000 if locked else 0)
    assert row["net_wealth"] == (100000 if locked else 80000)
    assert row["tax_event_cash"] == 0
    assert row["funding_failure"] == locked
