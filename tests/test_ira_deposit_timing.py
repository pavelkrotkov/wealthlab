"""Later receipts cannot backfill earlier unavailable IRA principal.

The annual Roth ordering pool includes later regular contributions, but the
cash ledger still rejects withdrawals before any IRA assets exist. A late
receipt must not rerun failed earlier deposit or withdrawal requests.
"""

from wealthlab.retirement.distribution_inputs import DistributionCase
from wealthlab.retirement.distributions import run
from wealthlab.retirement.ira_contribution_example import synthetic


def test_early_cash_shortfall_does_not_retry_deposit_after_withdrawal():
    data = synthetic().model_dump(mode="json")
    data["opening_cash"] = data["contributions"]["opening_cash"] = "1000"
    result = run(DistributionCase.model_validate(data))
    assert [r["funded"] for r in result["contribution_orders"]] == [1000, 0]
    assert sum(r["unfunded"] for r in result["contribution_orders"]) == 5000
    assert result["cash"] == 35000


def test_late_roth_deposit_joins_annual_ordering_without_earlier_cash():
    data = synthetic().model_dump(mode="json")
    for order in data["contributions"]["orders"]:
        order["date"] = "2026-12-15"
    result = run(DistributionCase.model_validate(data))
    assert result["orders"][-1]["additional_tax"] == 1200
    assert result["cash"] == 39000


def empty_opening(data):
    data["opening_cash"] = data["contributions"]["opening_cash"] = "0"
    for account in [*data["accounts"], *data["contributions"]["accounts"]]:
        account["balance"] = "0"
    person = data["owners"][0]
    person.update(
        federal_ira_basis="0",
        nj_ira_basis="0",
        roth_regular_basis="0",
        nj_roth_basis="0",
        roth_first_year=None,
        conversions=[],
    )


def test_future_deposits_cannot_fund_prior_withdrawals_or_conversions():
    data = synthetic().model_dump(mode="json")
    empty_opening(data)
    data["contributions"]["receipts"] = [
        dict(id="later_cash", provenance="illustration", date="2026-12-01", amount="6000")
    ]
    for order in data["contributions"]["orders"]:
        order["date"] = "2026-12-15"
    result = run(DistributionCase.model_validate(data))
    assert sum(r["paid"] for r in result["orders"]) == 0
    assert (result["cash"], sum(result["account_balances"].values())) == (0, 6000)
    assert result["owners"][0]["roth_first_year"] == 2026


def test_source_inputs_and_export_remain_unchanged():
    case = synthetic()
    before = case.model_dump_json()
    result = run(case)
    assert case.model_dump_json() == before
    assert run(DistributionCase.model_validate_json(before)) == result
