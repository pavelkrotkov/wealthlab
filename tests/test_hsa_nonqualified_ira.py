"""Actual nonqualified HSA income reaches IRA contribution MAGI and household tax cash."""

from wealthlab.household.projection import project
from wealthlab.retirement.hsa_distribution_example import synthetic


def test_hsa_income_increases_ira_magi_without_changing_wage_payroll_or_duplicate_cash():
    rows = project(synthetic())
    completed = [r for r in rows if r["ira_tax_reconciled"]]
    assert [r["ira_contribution_eligibility"]["traditional_ira_magi"] for r in completed] == [
        96000,
        76000,
    ]
    assert [r["annual_tax"]["federal"]["agi"] for r in completed] == [93000, 73000]
    assert [r["annual_tax"]["federal"]["employee_payroll"] for r in completed] == [4590, 4590]
    assert sum(r["tax_event_cash"] for r in rows) == 45000
    # The qualified-only control ends at155243; extra tax is10000*12% +10000*20%.
    assert rows[-1]["net_wealth"] == 152043
