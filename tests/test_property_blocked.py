"""A blocked close preserves home/lien, posts no unexecuted cash/tax and fails joint safety.

The cash, authorization-cap and lock cases all retain the property and actual
principal; later generic debt service continues rather than pretending that an
unexecuted sale removed a contractual payment. No sale is automatically retried.
"""

import pytest

from tests.property_cases import change, holding, negative, sale
from wealthlab.household.projection import project
from wealthlab.markets.household_outcomes import funding


def blocked(reason):
    def changed(data):
        negative(data)
        if reason == "cash":
            data["accounts"][0]["balance"] = "10000"
        if reason == "cap":
            sale(data)["maximum_owner_cash_to_close"] = "10000"
        if reason == "lock":
            holding(data)["observations"][5]["locked"] = True

    return change(changed)


@pytest.mark.parametrize("reason", ["cash", "cap", "lock"])
def test_blocked_close_is_atomic_and_normal_debt_service_continues(reason):
    rows = project(blocked(reason))
    close = rows[5]
    expected = dict(
        property_product_failure=True,
        property_closing_costs=0,
        property_owner_cash_paid=0,
        property_cash_received=0,
        property_debt_principal_paid=0,
        tax_event_cash=0,
        debt_payment=600,
    )
    assert {key: close[key] for key in expected} == expected
    assert close["property_closing_events"][0]["executed"] is False
    assert rows[-1]["account_balances"]["home"] == 300000
    assert rows[-1]["debt_balances"]["home_lien"] == 60000
    assert rows[-1]["closing_cash"] == (2800 if reason == "cash" else 12800)
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 0


@pytest.mark.parametrize("reason", ["cash", "cap", "lock"])
def test_a_required_blocked_exit_is_a_joint_failure_even_without_spending_shortfall(reason):
    outcome = funding(project(blocked(reason)))
    expected = dict(
        funded=False,
        product_feasible=False,
        joint_feasible=False,
        first_property_failure="2026-06-01",
        property_failure_months=7,
    )
    assert {key: outcome[key] for key in expected} == expected
    assert outcome["funding_shortfall"] == 0
