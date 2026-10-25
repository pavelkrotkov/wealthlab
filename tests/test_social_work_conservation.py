"""Matched forecasts and earned outcomes conserve cash plus remaining government position."""

from datetime import date

import pytest
from social_work_cases import calculate, payload


@pytest.mark.parametrize("actual", [0, 2400, 10000])
@pytest.mark.parametrize("forecast", [0, 2400, 10000])
def test_cash_plus_remaining_government_position_equals_net_entitlement(actual, forecast):
    data = payload()
    data["work"]["years"][0].update(
        actual_monthly_wages=[actual] * 12, forecast_monthly_wages=[forecast] * 12
    )
    data["work"]["overpayment_recovery_fraction"] = "0.10"
    result = calculate(data)
    end = date(data["claims"]["end_year"], 1, 1)
    ordinary = result["claims_counterfactual"]["total_issued_before_offsets"]
    deductions = sum(
        r["actual_deduction"]
        for r in result["monthly_work_assessments"]
        if r["payment_month"] < end
    )
    arf = sum(
        r["amount"] for r in result["reduction_factor_adjustments"] if r["payment_month"] < end
    )
    final = result["monthly_cash"][-1]
    net_position = final["government_receivable"] - final["government_overpayment_debt"]
    assert result["total_net_cash"] + net_position == ordinary - deductions + arf
