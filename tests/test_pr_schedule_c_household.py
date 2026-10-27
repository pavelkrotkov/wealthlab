"""The rounded binding credit changes real PR settlement after actual US payment."""

from decimal import Decimal

from pr_schedule_c_cases import household

from wealthlab.tax.jurisdiction_execution import evaluate


def test_native_household_pays_us475_and_actual_pr815_77_after_407_83_credit():
    result = evaluate(household())
    audit = result["country_assessments"]["es_income_2025"]
    final = result["rows"][-1]
    assert audit["actual_us_income_tax_paid"] == 475
    assert audit["assessment"]["regular_credit"]["allowed"] == Decimal("407.83")
    assert final["foreign_tax_paid"] == Decimal("815.77")
    assert final["annual_tax"]["federal"]["foreign_tax_credit"] == 0
    assert not final["funding_failure"]
