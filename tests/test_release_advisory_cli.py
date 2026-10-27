"""Matched native CLI/UI execution preserves actual fee cash and typed NJ losses.

The original well costs $100,000 and exits for $40,000; its net partnership
loss is $60,000. Actual monthly outer fees consume $1,105.97 separately from
native manager costs, leaving $138,894.03 from the original $200,000 capital.
"""

import json
from calendar import monthrange
from decimal import ROUND_HALF_UP, Decimal

from tests.release_advisory_cases import matched as matched
from wealthlab.household.report import encode
from wealthlab.tax.nj_business import BusinessLoss


def test_cli_and_ui_keep_identical_actual_common_fee_cash_and_original_capital(matched):
    profile, result, app, files = matched
    assert result == json.loads(encode(app.session_state["policy_search_result"]))
    row = result["selected_training"]["details"][0]["rows"][-1]
    assert sum(a.balance for a in profile.household.accounts) == 200000
    assert row["closing_cash"] == row["net_wealth"] == "138894.03"
    assert result["candidates"][0]["median_advisory_fees_paid"] == "1105.97"
    assert row["fees_owed"] == row["advisory_fees_owed"] == "0.00"
    assert files == ["original-synthetic-search.json"]


def test_actual_nj_loss_is_typed_in_execution_and_structured_in_cli_json(matched):
    _, result, app, _ = matched
    row = app.session_state["policy_search_result"]["selected_training"]["details"][0]["rows"][-1]
    assert row["annual_tax"]["new_jersey"]["business_carry"] == [
        BusinessLoss(year=2026, amount=60000)
    ]
    exported = result["selected_training"]["details"][0]["rows"][-1]
    assert exported["annual_tax"]["new_jersey"]["business_carry"] == [
        dict(year=2026, amount="60000.00")
    ]


def test_well_fee_cash_matches_independent_monthly_marginal_contract_arithmetic(matched):
    _, result, _, _ = matched
    cash = Decimal(100000)  # $200,000 opening less the actual $100,000 first-month call.
    for month in range(1, 13):
        property_value = Decimal(20000)
        if month == 12:
            cash += 40000
            property_value = Decimal(0)
        annual = 1000 + (cash + property_value - 100000) * Decimal(".005")
        bill = (annual * monthrange(2026, month)[1] / 365).quantize(
            Decimal(".01"), rounding=ROUND_HALF_UP
        )
        cash -= bill
    actual = result["selected_training"]["details"][0]["rows"][-1]
    assert cash == Decimal(actual["closing_cash"]) == Decimal("138894.03")
    assert 140000 - cash == Decimal(result["candidates"][0]["median_advisory_fees_paid"])
