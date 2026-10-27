"""The rounded mixed limit changes real settlement while source cash and payroll stay fixed.

US taxable W2:3000000-13125=2986875, US tax1062164. PR ordinary
2996500 yields937678.50, plus600000*15%=1027678.50.
Gross US source83.33% allocates2916.55 exemption; net source2997083.45.
The country limit856364.49 binds below both actual US payment and aggregate
limit856398.78, leaving actual PR171314.01. Continuous source ratios would
instead claim856398.75 and leave171279.75, understating the paid bill34.26.
"""

from decimal import Decimal

from pr_schedule_c_mixed_household import binding_mixed

from wealthlab.tax.jurisdiction_execution import evaluate


def test_binding_mixed_credit_changes_actual_household_tax_by_34_26():
    result = evaluate(binding_mixed())
    audit = result["country_assessments"]["es_income_2025"]
    final = result["rows"][-1]
    credit = audit["assessment"]["regular_credit"]
    assert audit["actual_us_income_tax_paid"] == 1062164
    assert credit["allowed"] == Decimal("856364.49")
    assert credit["total_limitation"] == Decimal("856398.78")
    assert final["foreign_tax_paid"] == Decimal("171314.01")
    assert final["lot_audit"]["disposals"][0]["proceeds"] == 700000
    assert not final["funding_failure"]
