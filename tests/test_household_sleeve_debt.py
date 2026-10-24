"""Negative sleeve equity becomes one household liability, including after liquidation."""

from household_sleeve_cases import change, flat

from wealthlab.household.projection import project


def squeeze(data):
    data["sleeve_plan"]["sleeves"][0]["observations"][0]["short_return"] = "4"


def test_margin_cash_and_recoursedebt_reconcile_to_total_economic_loss():
    case = change(flat(), squeeze)
    rows = project(case)
    first = rows[0]
    assert first["closing_cash"] == 0
    assert first["account_balances"]["sleeve"] == 0
    assert first["sleeve_liability"] == 10000
    assert first["net_wealth"] == -10000
    assert first["funding_shortfall"] == 0
    assert first["funding_failure"]
    assert rows[-1]["net_wealth"] == -10000


def test_later_actual_receipts_repay_closed_account_debt_once():
    case = change(flat(), squeeze)

    def add_receipt(data):
        data["tax_plan"]["events"] = [
            dict(
                date="2026-02-01",
                description="External cash illustration",
                cash_received="3000",
                federal={},
                new_jersey={},
            )
        ]

    rows = project(change(case, add_receipt))
    assert rows[1]["sleeve_liability"] == 7000
    assert rows[1]["closing_cash"] == 0
    assert rows[1]["net_wealth"] == -7000
    assert rows[-1]["sleeve_audit"][1]["recourse_debt_paid"] == 3000
    assert sum(r["tax_event_cash"] for r in rows) == 3000
