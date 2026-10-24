"""Entitled income is an asset before payment, but cannot finance an early cash target."""

from datetime import date

from wealthlab.retirement.hsa_investment_example import synthetic
from wealthlab.retirement.hsa_investment_inputs import HSAInvestments
from wealthlab.retirement.hsa_investment_reporting import snapshot
from wealthlab.retirement.hsa_investments import Ledger


def test_receivable_payment_preserves_wealth_and_original_year_recognition():
    data = synthetic().model_dump(mode="json")
    data["case"]["end"] = "2027-01-31"
    data["cash_targets"] = []
    data["marks"].append(dict(date="2026-12-31", prices=dict(fund="110")))
    late = dict(
        data["case"]["distributions"][0],
        id="late",
        ex_date="2026-12-20",
        recognition_date="2026-12-20",
        payment_date="2027-01-15",
    )
    data["case"]["distributions"].append(late)
    ledger = Ledger(HSAInvestments.model_validate(data))
    ledger.advance(date(2026, 12, 31))
    before = snapshot(ledger)
    ledger.advance(date(2027, 1, 15))
    after = snapshot(ledger)
    assert before["distribution_receivable"] == {"hsa": 70}
    assert before["cash_by_account"]["hsa"] == 3947
    assert after["cash_by_account"]["hsa"] == 4017
    assert after["distribution_receivable"] == {"hsa": 0}
    assert before["net_wealth"] == after["net_wealth"] == 11717
    check_years(after)


def check_years(result):
    assert result["nj_income_by_year"][2026]["dividends"] == 170
    assert result["nj_income_by_year"][2027] == dict(interest=0, dividends=0, dispositions=0)
