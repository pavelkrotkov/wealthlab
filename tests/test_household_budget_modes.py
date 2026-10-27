"""Unused forecasts do not affect retained portfolios; incomplete actual years remain labeled."""

from datetime import date

import pytest

from tests.household_budget_cases import synthetic
from wealthlab.household.funding import Wallet
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_book import Ledger
from wealthlab.portfolio.household_budget import context
from wealthlab.portfolio.tax_budget import impact


def test_dormant_unconfirmed_forecast_has_no_effect_without_a_budget_policy():
    data = synthetic().model_dump(mode="json")
    # A retained-portfolio comparison keeps forecast inputs fixed but does not
    # claim any benefit from unused or unconfirmed quote assumptions.
    data["lot_plan"]["case"]["sale_policies"] = []
    data["lot_plan"]["tax_budget_forecasts"][0]["fixed_forecast_deductions_confirmed"] = False
    final = project(Scenario.model_validate(data))[-1]
    assert final["closing_cash"] == 1000
    assert final["net_wealth"] == 11000
    assert final["lot_audit"]["budget_audit"] == []


def test_partial_actual_year_is_not_presented_as_a_completed_annual_return():
    data = synthetic().model_dump(mode="json")
    # An annual forecast remains a forecast even when only six actual months
    # have been observed; partial liability is not a completed-return result.
    data["end"] = "2026-07-01"
    data["lot_plan"]["case"]["end"] = "2026-06-30"
    data["lot_plan"]["monthly_marks"] = data["lot_plan"]["monthly_marks"][:6]
    final = project(Scenario.model_validate(data))[-1]
    record = final["lot_audit"]["budget_audit"][0]
    assert record["actual_return_status"] == "partial"
    assert record["cash_observed_through"] == "2026-06-30"
    assert record["estimated_delta_at_decision"] == 500


def test_market_liquidity_lock_blocks_actual_sale_without_forecast_cash():
    case = synthetic()
    lots, wallet = Ledger(case), Wallet(case)
    lots.locked.add("stock")
    lots.after_receipts(wallet, date(2026, 1, 1), date(2026, 2, 1))
    assert lots.sale_decisions[0]["status"] == "blocked by market liquidity lock"
    assert lots.sale_decisions[0]["forecast_id"] == "illustrative_full_annual_forecast"
    assert wallet.cash == 1000
    assert not lots.book.history


def test_observation_quote_cannot_include_a_future_tax_year():
    case = synthetic()
    lots = Ledger(case)
    view, _source = context(case.lot_plan, case.lot_plan.case.sale_policies[0])
    with pytest.raises(ValueError, match="future tax year"):
        impact(view, lots.book, date(2026, 1, 31), through_year=2027)


def test_past_year_without_a_forecast_is_not_silently_replaced_by_another_year():
    case = synthetic()
    lots = Ledger(case)
    view, _source = context(case.lot_plan, case.lot_plan.case.sale_policies[0])
    with pytest.raises(ValueError, match="requested observed year"):
        impact(view, lots.book, date(2026, 12, 31), through_year=2025)
