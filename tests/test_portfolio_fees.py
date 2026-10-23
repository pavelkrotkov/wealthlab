"""Recurring fees conserve cash plus holdings less unpaid obligations in both comparisons."""

from fee_cases import fee_case, fee_schedule
from test_harvest_comparison import harvest_case

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


def test_recurring_fees_charge_each_explicit_period_once():
    """Two ten-day periods each cost $10 on $1,000 of assets plus a $5 fixed fee.

    Assessments are dated events, so the closing snapshot cannot repeat a charge.
    Cash and total wealth must both fall by the two-period $30 expense.
    """
    payload = fee_case()
    payload["fee_schedules"][0]["periods"].append(
        dict(
            start="2026-01-11",
            date="2026-01-21",
            prices={"STOCK": "10", "ETF": "10"},
        )
    )
    result = run(LotCase.model_validate(payload))
    assert result["closing_cash"] == 970
    assert result["gross_wealth"] == 1970
    assert result["fee_summary"] == dict(
        cash_assessed=30,
        cash_paid=30,
        cash_owed=0,
        embedded_estimate=0,
    )


def test_same_date_cash_inclusive_bases_are_independent_of_schedule_order():
    payload = fee_case()
    first = fee_schedule(include_cash=True, fixed_per_period="0")
    second = dict(first, id="custody", kind="custody", annual_rate="0.1825")
    payload["fee_schedules"] = [first, second]
    forward = run(LotCase.model_validate(payload))
    payload["fee_schedules"].reverse()
    reverse = run(LotCase.model_validate(payload))
    assert forward["closing_cash"] == reverse["closing_cash"] == 970
    assert [row["valuation_base"] for row in forward["fee_assessments"]] == [2000, 2000]


def test_embedded_fee_estimates_do_not_charge_prices_twice():
    payload = fee_case()
    payload["fee_schedules"][0]["treatment"] = "embedded_in_prices"
    result = run(LotCase.model_validate(payload))
    assert result["gross_wealth"] == 2000
    assert result["fee_summary"]["embedded_estimate"] == 15
    assert result["fee_summary"]["cash_assessed"] == 0


def test_matched_comparison_applies_manager_fees_only_to_the_owned_sleeve():
    payload = harvest_case()
    schedule = fee_schedule(kind="manager", security_ids=["ETF"], fixed_per_period="0")
    schedule["periods"] = [
        dict(
            start="2026-06-01",
            date="2026-06-11",
            prices={"STOCK": "10", "ETF": "10"},
        )
    ]
    payload["fee_schedules"] = [schedule]
    result = run(LotCase.model_validate(payload))
    holding = result["harvest_comparison"]["holding"]
    assert holding["extra_cash_fees"] == 10
    assert holding["gross_wealth_difference"] == -10
    assert holding["tax_adjusted_difference"] == 45
