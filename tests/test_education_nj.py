"""NJ deduction history and final NJ gross income cannot be inferred from federal earnings.

Previously deducted contributions can be taxable principal in NJ. The model
must preserve unknown recapture until the user supplies its history, while the
income threshold independently controls the potential funded contribution deduction.
"""

from decimal import Decimal

import pytest

from tests.test_education_cash import calculate, payload


def test_supplied_nj_recapture_adds_previously_deducted_principal():
    data = payload()
    data["allocations"][0]["nj_recaptured_contributions"] = 1000
    parent = calculate(data)["annual_tax_groups"][0]
    assert parent["nj_total_income"] == Decimal("2536.80")
    data["allocations"][0]["nj_recaptured_contributions"] = 4000
    with pytest.raises(ValueError, match="returned nonqualified principal"):
        calculate(data)


@pytest.mark.parametrize(("income", "deduction"), [(200000, 10000), (200001, 0), (None, None)])
def test_njbest_threshold_uses_supplied_nj_gross_income(income, deduction):
    data = payload()
    data["nj_gross_income"] = income
    assert calculate(data)["njbest_potential_deduction"] == deduction


def test_other_plans_have_no_njbest_deduction_or_principal_recapture():
    data = payload()
    data["plans"][0]["njbest"] = False
    result = calculate(data)
    assert result["njbest_potential_deduction"] == 0
    assert result["annual_tax_groups"][0]["nj_total_income"] == Decimal("1536.80")
    data["allocations"][0]["nj_recaptured_contributions"] = 1
    with pytest.raises(ValueError, match="another plan"):
        calculate(data)


def test_missing_recapture_stays_unknown_and_contributions_have_no_federal_deduction():
    result = calculate(payload())
    assert result["annual_tax_groups"][0]["nj_total_income"] is None
    assert result["njbest_funded_contributions"] == 12000
    assert result["federal_contribution_deduction"] == 0
