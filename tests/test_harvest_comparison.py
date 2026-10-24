"""Matched harvesting isolates basis deferral from prices, trading costs and terminal exit."""

from decimal import Decimal as D

from test_tax_budget_policy import budget_case

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


def harvest_case():
    payload = budget_case()
    payload["sale_policies"] = []
    payload["lots"][0].update(federal_basis="1000", nj_basis="1000", economic_basis="1000")
    payload["securities"].append(
        dict(payload["securities"][0], id="ETF", wash_group="ETF", kind="etf")
    )
    payload["closing_prices"] = {"STOCK": "10", "ETF": "10"}
    payload["harvest_policies"] = [
        dict(
            id="harvest",
            provenance="assumption",
            date="2026-06-01",
            account_id="brokerage",
            security_id="STOCK",
            replacement_id="ETF",
            replacement_eligible=True,
            prices={"STOCK": "7.5", "ETF": "7.5"},
        )
    ]
    payload["compare_harvesting"] = True
    payload["terminal_exit"] = dict(account_ids=["brokerage"], no_replacements_next30_days=True)
    return payload


def test_same_year_recovery_and_exit_reverses_the_initial_tax_saving():
    """Selling at 750 and rebuying a distinct sleeve lowers basis from 1000 to 750.

    With equal recovery to 1000, marked wealth is unchanged. The apparent $55
    holding-period benefit disappears when both portfolios exit in the same year.
    """
    result = run(LotCase.model_validate(harvest_case()))
    comparison = result["harvest_comparison"]
    assert result["gross_wealth"] == 2000
    assert result["harvest_decisions"][0]["sold_units"] == 100
    assert comparison["holding"]["total_tax_saving"] == 55
    assert comparison["holding"]["gross_wealth_difference"] == 0
    assert comparison["terminal_exit"]["total_tax_saving"] == 0
    assert comparison["terminal_exit"]["tax_adjusted_difference"] == 0
    assert not result["terminal_exit"]["lots"]


def test_replacement_underperformance_is_not_reported_as_tax_alpha():
    payload = harvest_case()
    payload["closing_prices"]["ETF"] = "9"
    comparison = run(LotCase.model_validate(payload))["harvest_comparison"]
    assert comparison["holding"]["gross_wealth_difference"] == -100
    assert comparison["holding"]["tax_adjusted_difference"] == -45
    assert comparison["terminal_exit"]["tax_adjusted_difference"] == -78


def test_harvest_commissions_use_only_sale_proceeds_and_reduce_marked_wealth():
    payload = harvest_case()
    payload["harvest_policies"][0]["commission_per_trade"] = "1"
    payload["closing_prices"] = {"STOCK": "7.5", "ETF": "7.5"}
    result = run(LotCase.model_validate(payload))
    assert result["closing_cash"] == 1000
    assert result["transaction_costs"] == 2
    assert result["harvest_comparison"]["holding"]["gross_wealth_difference"] == -2
    assert result["harvest_comparison"]["holding"]["extra_transaction_costs"] == 2
    assert D(result["lots"][0]["federal_basis"]) == 749


def test_partial_cap_preserves_unsold_original_shares_and_basis():
    payload = harvest_case()
    payload["harvest_policies"][0]["max_gross_sales"] = "375"
    result = run(LotCase.model_validate(payload))
    original = next(lot for lot in result["lots"] if lot["id"] == "original")
    assert D(original["quantity"]) == 50
    assert D(original["federal_basis"]) == 500
    assert result["harvest_loss_summary"]["federal_recognized_gain"] == -125
    assert result["harvest_comparison"]["holding"]["total_tax_saving"] == D("27.50")
