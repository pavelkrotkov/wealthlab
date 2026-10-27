"""Stored cash stays immutable; later cash never becomes an earlier actual payment."""

from datetime import date
from decimal import Decimal

from tests.advisory_cases import change, plain
from tests.advisory_snapshot_cases import snapshot_fee
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_two_schedules_use_one_completed_cash_snapshot_after_an_actual_earlier_bill():
    household = plain(cash="1000", asset="0").model_copy(update=dict(end=date(2026, 3, 1)))
    case = snapshot_fee(household, account="cash", rate=".12")

    def later_bills(plan):
        for identity in ("second", "third"):
            schedule = plan["schedules"][0].copy()
            schedule["id"] = identity
            schedule["periods"] = [
                dict(
                    accrual_start="2026-02-01",
                    accrual_end="2026-03-01",
                    valuation_date="2026-01-31",
                    valuation_cutoff="completed_month_end",
                    assessment_date="2026-02-28",
                    payment_due_date="2026-02-28",
                )
            ]
            plan["schedules"].append(schedule)

    rows = project(change(case, later_bills))
    assert rows[0]["advisory_fees_paid"] == 10
    assert [a["valuation_base"] for a in rows[1]["advisory_fee_assessments"]] == [990, 990]
    assert rows[1]["advisory_fees_paid"] == Decimal("18.48")
    assert rows[1]["closing_cash"] == Decimal("971.52")


def test_later_actual_receipt_pays_advance_arrears_on_its_real_month_end():
    data = plain(cash="0").model_dump(mode="json")
    data["end"] = "2026-05-01"
    data["incomes"] = [
        dict(
            id="later",
            provenance="illustration",
            owner="person_a",
            start="2026-02-01",
            end="2026-03-01",
            monthly_amount="1000",
            currency="USD",
            annual_growth=0,
            stop_at_retirement=False,
        )
    ]
    case = snapshot_fee(
        Scenario.model_validate(data), start="2026-02-01", end="2026-05-01", advance=True
    )
    rows = project(case)
    assert rows[0]["advisory_fees_paid"] == 0
    assert rows[0]["advisory_fees_owed"] == Decimal("247.22")
    assert rows[1]["advisory_fees_paid"] == Decimal("247.22")
    assert rows[-1]["net_wealth"] == Decimal("100752.78")
    payments = rows[-1]["advisory_fee_audit"]["payments"]
    assert [(p["date"], p["paid"]) for p in payments[:2]] == [
        ("2026-01-31", 0),
        ("2026-02-28", Decimal("247.22")),
    ]
