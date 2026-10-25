"""Independent FRA cutoff, floor-dollar excess and first non-service-year checks."""

from datetime import date

from social_work_cases import calculate, payload, work


def test_first_non_service_year_preserves_low_wage_months_despite_full_year_wages():
    data = payload()
    data["claims"]["members"][0]["claim_month"] = "2026-07-01"
    wages = [10000] * 6 + [2040] * 6
    data["work"]["years"][0].update(forecast_monthly_wages=wages, actual_monthly_wages=wages)
    result = calculate(data)
    assert work(result, 2026)["actual_grace_year"]
    assert work(result, 2026)["actual_charged"] == 0
    assert not work(result, 2027)["actual_grace_year"]
    assert result["monthly_cash"][7]["forecast_withheld"] == 0


def test_prior_grace_usage_prevents_electing_another_monthly_test():
    data = payload()
    data["claims"]["members"][0]["claim_month"] = "2026-07-01"
    data["work"]["grace_used_before_projection"]["worker"] = True
    wages = [10000] * 6 + [2040] * 6
    data["work"]["years"][0].update(forecast_monthly_wages=wages, actual_monthly_wages=wages)
    result = calculate(data)
    assert not work(result, 2026)["actual_grace_year"]
    assert work(result, 2026)["actual_charged"] > 0


def test_zero_benefit_entitlement_still_uses_the_initial_grace_year():
    data = payload()
    data["claims"]["members"][0]["pia_january_2026"] = 0
    result = calculate(data)
    assert work(result, 2027)["actual_grace_year"]
    assert not work(result, 2028)["actual_grace_year"]
    assert result["total_net_cash"] == 0
    assert result["monthly_cash"][-1]["payment_month"] == date(2032, 12, 1)
