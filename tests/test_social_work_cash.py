"""POMS own-record $562/$2881/$491 oracle, causal forecasts and real overpayment debt."""

from decimal import Decimal as D

from social_work_cases import calculate, cash, payload, work


def test_closed_year_partial_month_is_a_receivable_before_later_cash():
    result = calculate(payload())
    assessment = work(result, 2026)
    assert assessment["forecast_cash_withheld"] == 3372
    assert assessment["actual_charged"] == 2881
    assert assessment["crediting_months"] == 6
    assert not assessment["actual_grace_year"]


def test_partial_month_claim_is_paid_only_in_the_assumed_later_month():
    result = calculate(payload())
    december = cash(result, 2026, 12)
    assert december["net_cash"] == 562
    assert december["government_receivable"] == 491
    assert cash(result, 2027, 4)["refund_cash"] == 0
    assert cash(result, 2027, 5)["refund_cash"] == 491
    assert cash(result, 2027, 5)["net_cash"] == 1053


def test_actual_future_wages_cannot_change_prior_cash_or_positions():
    data = payload()
    original = calculate(data)
    data["work"]["years"][0]["actual_monthly_wages"][-1] = 100000
    changed = calculate(data)
    assert original["monthly_cash"][:11] == changed["monthly_cash"][:11]
    assert cash(changed, 2026, 12)["government_overpayment_debt"] == 2810
    assert cash(changed, 2027, 4)["recovered_overpayment"] == 0
    assert cash(changed, 2027, 5)["net_cash"] == 0
    assert cash(changed, 2027, 5)["government_overpayment_debt"] == 2810
    # Final December was not actually paid until January: its additional
    # overpayment appears only when that cash occurs, not in December debt.
    assert cash(changed, 2026, 12)["net_cash"] == 562


def test_underestimated_earnings_leave_debt_and_respect_conditional_recovery_fraction():
    data = payload()
    data["work"]["years"][0]["forecast_monthly_wages"] = [0] * 12
    data["work"]["overpayment_recovery_fraction"] = "0.50"
    result = calculate(data)
    assert cash(result, 2026, 12)["government_overpayment_debt"] == 2881
    assert cash(result, 2027, 5)["net_cash"] == 281
    assert cash(result, 2027, 5)["government_overpayment_debt"] == 2600
    assert min(r["net_cash"] for r in result["monthly_cash"]) >= D(0)


def test_reduction_factor_credits_include_partial_month_and_pay_arrears_only_later():
    result = calculate(payload())
    assert cash(result, 2031, 2)["net_cash"] == 562
    assert cash(result, 2031, 12)["government_receivable"] == 220
    assert cash(result, 2032, 4)["net_cash"] == 562
    assert cash(result, 2032, 5)["current_arf_increase"] == 20
    assert cash(result, 2032, 5)["refund_cash"] == 300
    assert cash(result, 2032, 5)["net_cash"] == 882
    assert cash(result, 2032, 6)["net_cash"] == 582
