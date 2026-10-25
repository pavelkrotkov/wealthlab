"""Sequential schedules and cent-settled caps must remain valid after execution."""

from decimal import Decimal

import pytest
from rebalance_cases import book_case, payload

from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_validation import validate
from wealthlab.portfolio.rebalance import decide
from wealthlab.portfolio.rebalance_orders import sell


def test_later_policy_cannot_omit_a_prior_rebalance_purchase():
    data = payload()
    plan = data["lot_plan"]
    plan["rebalances"].append(
        dict(plan["rebalances"][0], id="later", date="2026-04-30", target_weights=dict(stock="1"))
    )
    with pytest.raises(ValueError, match="every account holding"):
        validate(Scenario.model_validate(data))


def test_unused_zero_weight_target_need_not_be_repeated():
    data = payload()
    plan = data["lot_plan"]
    plan["rebalances"][0]["target_weights"] = dict(stock="1", bond="0")
    plan["rebalances"].append(
        dict(plan["rebalances"][0], id="later", date="2026-04-30", target_weights=dict(stock="1"))
    )
    validate(Scenario.model_validate(data))


def test_sale_budget_tracks_actual_cent_settled_gross():
    book, policy, _ = book_case()
    gross = sell(book, policy, "stock", Decimal("99.997"), Decimal(500))
    assert gross == book.cash[policy.account_id]


def test_fractional_cent_sale_cap_cannot_be_exceeded_by_rounding():
    book, policy, prices = book_case(max_sale_fraction=".1")
    prices["stock"] = Decimal("100.009")
    result = decide(book, policy, prices, set())
    assert result["gross_sales"] <= result["opening_security_value"] * Decimal(".1")
