"""Opening and completed native 529 values are distinct from later in-month returns."""

from decimal import Decimal

from tests.advisory_cases import change
from tests.advisory_snapshot_cases import snapshot_fee
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.education_household_example import synthetic


def test_529_opening_and_previous_completed_snapshots_do_not_preview_later_returns():
    data = synthetic().model_dump(mode="json")
    data.update(incomes=[], expenses=[], hsa_plan=None, ira_plan=None)
    data["tax_plan"]["income_rules"] = []
    accounts = {a["id"]: a for a in data["accounts"]}
    data["accounts"] = [accounts["cash"], accounts["college"]]
    data["accounts"][0]["balance"] = "1000"
    plan = data["education_plan"]
    plan["contributions"], plan["tuition"] = [], []
    plan["returns"] = [
        dict(
            id="june", provenance="illustration", date="2026-06-15", account_id="college", rate=".1"
        ),
        dict(
            id="july",
            provenance="illustration",
            date="2026-07-15",
            account_id="college",
            rate="-.5",
        ),
    ]
    case = snapshot_fee(
        Scenario.model_validate(data),
        account="college",
        valued="2026-06-01",
        billed="2026-06-30",
        start="2026-06-01",
        end="2026-07-01",
    )

    def second_fee(plan):
        second = plan["schedules"][0].copy()
        second["id"] = "previous_completed"
        second["periods"] = [
            dict(
                accrual_start="2026-07-01",
                accrual_end="2026-07-31",
                valuation_date="2026-06-30",
                valuation_cutoff="completed_month_end",
                assessment_date="2026-07-31",
                payment_due_date="2026-07-31",
            )
        ]
        plan["schedules"].append(second)

    rows = project(change(case, second_fee))
    assert rows[5]["advisory_fee_assessments"][0]["valuation_base"] == 30000
    assert rows[5]["advisory_fees_paid"] == 25
    assert rows[6]["advisory_fee_assessments"][0]["valuation_base"] == 33000
    assert rows[6]["advisory_fees_paid"] == Decimal("27.50")
    assert rows[6]["account_balances"]["college"] == 16500
    assert rows[-1]["net_wealth"] == Decimal("17447.50")
