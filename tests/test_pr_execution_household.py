"""Raw worldwide recognition and PR-excluded federal tax execute in the same wallet.

The country assessment remains a supplied 10,000 in these execution checks;
its legal calculation is intentionally outside the prepared-policy seam.
Source identity and actual cash still reconcile without a duplicate payroll
payment, a second US credit or an implicit change in independent NJ basis.
"""

from decimal import Decimal

from pr_execution_helpers import household

from wealthlab.household.projection import project


def test_excluded_income_still_pays_actual_foreign_tax_but_blocks_invalid_us_credit_claim():
    rows = project(household())
    final = rows[-1]
    assert sum(r["foreign_tax_paid"] for r in rows) == 10000
    assert final["annual_tax"]["federal"]["foreign_tax_credit"] == 0
    assert final["annual_tax"]["federal"]["income_tax"] == Decimal("4816.50")
    assert final["annual_tax"]["federal"]["employee_payroll"] == 7650
    assert final["funding_failure"]
    assert any("PR-excluded" in r for r in final["foreign_tax_unresolved"])


def test_denied_excluded_tax_credit_keeps_economics_and_known_us_nj_taxes_without_duplicate_cash():
    rows = project(household(credit_eligibility="denied"))
    final = rows[-1]
    assert final["annual_tax"]["new_jersey"]["income_tax"] == 4182
    assert final["closing_cash"] == Decimal("31001.50")
    assert final["net_wealth"] == final["closing_cash"]
    assert not final["funding_failure"]
    assert final["foreign_tax_source_identities"]


def test_included_government_wages_use_native_credit_without_losing_worldwide_payroll():
    rows = project(household(government=True))
    final = rows[-1]
    assert final["annual_tax"]["federal"]["foreign_tax_credit"] == Decimal("6724.50")
    assert final["annual_tax"]["federal"]["employee_payroll"] == 7650
    assert final["closing_cash"] == Decimal("29093.50")
    assert not final["funding_failure"]


def test_bare_us_exclusion_cannot_silently_omit_the_pr_household_tax_liability():
    import pytest

    scenario = household(credit_eligibility="denied")
    with pytest.raises(ValueError, match="shared country-tax cash book"):
        project(scenario.model_copy(update=dict(foreign_tax_plan=None)))


def test_a_different_country_assessment_does_not_cover_the_pr_household_tax_year():
    import pytest

    scenario = household(credit_eligibility="denied")
    plan = scenario.foreign_tax_plan
    assessment = plan.assessments[0].model_copy(update=dict(country="ES"))
    scenario = scenario.model_copy(
        update=dict(foreign_tax_plan=plan.model_copy(update=dict(assessments=[assessment])))
    )
    with pytest.raises(ValueError, match="PR assessment coverage"):
        project(scenario)
