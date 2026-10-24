"""Credits earned during a pre70 claim year wait for January entitlement, paid in February."""

from datetime import date

from tests.test_social_cash import calculate, payload


def single_case(birth="1960-07-02", claim="2028-07-01"):
    data = payload()
    data.update(start_year=2028, end_year=2030)
    data["members"] = [data["members"][1]]
    data["members"][0].update(
        birth_date=birth, claim_month=claim, partner=None, spousal_eligibility_confirmed=False
    )
    return data


def test_pre70_claim_year_credits_are_not_immediately_spendable():
    rows = calculate(single_case())["cash_months"]
    by_month = {row["payment_month"]: row for row in rows}
    assert by_month[date(2028, 8, 1)]["issued_before_offsets"] == 1040
    assert by_month[date(2029, 1, 1)]["issued_before_offsets"] == 1040
    assert by_month[date(2029, 2, 1)]["issued_before_offsets"] == 1080


def test_current_year_credits_are_recognized_at70_without_waiting_for_january():
    rows = calculate(single_case(claim="2030-07-01") | dict(end_year=2031))["cash_months"]
    first = next(r for r in rows if r["issued_before_offsets"])
    assert first["payment_month"] == date(2030, 8, 1)
    assert first["issued_before_offsets"] == 1240


def test_claiming_after70_does_not_earn_more_credits():
    rows = calculate(single_case(claim="2031-07-01") | dict(end_year=2033))["cash_months"]
    first = next(r for r in rows if r["issued_before_offsets"])
    assert first["issued_before_offsets"] == 1240
