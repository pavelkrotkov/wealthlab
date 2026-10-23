"""Unpaid fees reduce wealth once and receive later proceeds before reinvestment."""

from fee_cases import fee_case

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


def test_later_sale_settles_the_old_fee_without_creating_a_second_expense():
    """A $15 debt reduces $1,000 of shares to $985 net wealth before any payment.

    Selling $100 later leaves $900 of shares and $85 cash after paying the debt.
    The fee is an expense once; settlement changes its funding, not its amount.
    """
    payload = fee_case()
    payload["accounts"][0]["cash"] = "0"
    before = run(LotCase.model_validate(payload))
    assert before["fee_summary"]["cash_owed"] == 15
    assert before["gross_wealth"] == 985
    payload["trades"] = [
        dict(
            id="fund_fee",
            provenance="assumption",
            date="2026-03-01",
            action="sell",
            account_id="brokerage",
            security_id="STOCK",
            quantity="10",
            price="10",
            commission="0",
        )
    ]
    after = run(LotCase.model_validate(payload))
    assert after["closing_cash"] == 85
    assert after["fee_summary"]["cash_owed"] == 0
    assert after["fee_summary"]["cash_paid"] == 15
    assert after["gross_wealth"] == 985


def test_terminal_exit_pays_unpaid_fees_from_proceeds_once():
    payload = fee_case()
    payload["accounts"][0]["cash"] = "0"
    payload["terminal_exit"] = dict(account_ids=["brokerage"])
    result = run(LotCase.model_validate(payload))
    assert result["terminal_exit"]["closing_cash"] == 985
    assert result["terminal_exit"]["gross_wealth"] == result["gross_wealth"] == 985
    assert result["fee_summary"]["cash_owed"] == 15
    assert result["terminal_exit"]["fee_summary"]["cash_owed"] == 0


def test_harvesting_reserves_existing_fee_debt_before_buying_replacements():
    from fee_cases import fee_schedule
    from test_harvest_comparison import harvest_case

    payload = harvest_case()
    payload["accounts"][0]["cash"] = "0"
    payload["fee_schedules"] = [fee_schedule()]
    result = run(LotCase.model_validate(payload))
    assert result["fee_summary"]["cash_paid"] == 15
    assert result["fee_summary"]["cash_owed"] == 0
    assert result["harvest_decisions"][0]["replacement_units"] == 98
    assert result["closing_cash"] == 0
