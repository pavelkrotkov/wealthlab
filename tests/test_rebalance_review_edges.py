"""Sequential schedules and cent-settled caps must remain valid after execution."""

from decimal import Decimal

import pytest
from rebalance_cases import book_case, payload

from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_validation import validate
from wealthlab.portfolio.rebalance import decide


def test_later_policy_cannot_omit_a_prior_rebalance_purchase():
    data = payload()
    plan = data["lot_plan"]
    plan["rebalances"].append(
        dict(plan["rebalances"][0], id="later", date="2026-04-30", target_weights=dict(stock="1"))
    )
    with pytest.raises(ValueError, match="every account holding"):
        validate(Scenario.model_validate(data))


def test_fractional_cent_sale_cap_cannot_be_exceeded_by_rounding():
    book, policy, prices = book_case(max_sale_fraction=".1")
    prices["stock"] = Decimal("100.009")
    result = decide(book, policy, prices, set())
    assert result["gross_sales"] <= result["opening_security_value"] * Decimal(".1")
