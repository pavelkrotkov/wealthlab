"""The declared noninvestment classification changes MAGI without adding an investment base."""

from hsa_distribution_cases import change, flat

from wealthlab.household.projection import project


def test_hsa_withdrawal_is_not_an_investment_or_payroll_receipt_under_the_selected_assumption():
    def configure(data):
        data["tax_plan"]["events"] = [
            dict(
                date="2026-01-01",
                description="Synthetic wages and interest",
                cash_received="330000",
                federal=dict(wages_primary="300000", interest="30000"),
                new_jersey=dict(wages="300000", interest="30000"),
            )
        ]

    rows = project(change(flat(requested=10000), configure))
    fed = rows[-1]["annual_tax"]["federal"]
    assert (fed["agi"], fed["niit"], fed["additional_medicare"]) == (340000, 1140, 450)
    assert sum(r["tax_event_cash"] for r in rows) == 330000
    assert sum(r["hsa_additional_tax"] for r in rows) == 2000
    assert rows[-1]["net_wealth"] == 440000 - rows[-1]["annual_tax"]["total_liability"]
