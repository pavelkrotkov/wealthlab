"""Actually unpaid HSA custody fees reduce the historical fee base and remain native liabilities."""

from tests.advisory_snapshot_cases import snapshot_fee
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_invested_example import synthetic


def test_observed_hsa_opening_equity_subtracts_only_actual_unpaid_custodian_debt():
    data = synthetic().model_dump(mode="json")
    data["accounts"][0]["balance"] = "1000"
    data["hsa_plan"]["medical_bills"] = []
    book = data["hsa_plan"]["investments"]["case"]
    book["distributions"] = []
    book["fee_schedules"][0]["fixed_per_period"] = "350"
    book["closing_prices"]["fund"] = "100"
    case = snapshot_fee(
        Scenario.model_validate(data),
        account="hsa",
        cutoff="opening",
        valued="2026-02-01",
        billed="2026-02-28",
        start="2026-02-01",
        end="2026-03-01",
        rate=".12",
    )
    rows = project(case)
    # $100 inside cash pays only part of the $350 custody bill; no forced sale.
    # $10k actual assets -$250 unpaid debt = $9,750 opening net equity.
    assert rows[0]["account_balances"]["hsa"] == 10000
    assert rows[0]["hsa_investment_fees_owed"] == 250
    bill = rows[1]["advisory_fee_assessments"][0]
    assert bill["valuation_base"] == 9750
    assert bill["assessed"] == rows[1]["advisory_fees_paid"] == 91
    snapshot = rows[-1]["advisory_fee_audit"]["observed_snapshots"][0]
    assert snapshot["observed_account_fee_debt"] == dict(hsa=250)
    assert rows[-1]["net_wealth"] == 10659
