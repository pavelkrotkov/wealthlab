"""The spouse amount starts only when both ordinary claim applications allow it.

An early own claim keeps its original reduction when a later spouse add-on
starts at FRA. Reducing the combined amount again would underpay the recipient.
Uninsured spouses need no own PIA but do require an insured partner's record.
"""

from datetime import date
from decimal import Decimal

from tests.test_social_cash import calculate, cash_row, payload


def test_reduced_own_benefit_and_reduced_spouse_excess_are_not_reduced_as_one_amount():
    data = payload()
    data.update(start_year=2026, end_year=2027)
    for person in data["members"]:
        person["claim_month"] = "2022-01-01"
    low = next(r for r in calculate(data)["cash_months"] if r["member"] == "spouse")
    assert low["own_with_delayed_credits"] == 700
    assert low["spousal_excess"] == Decimal("162.50")
    assert low["entitlement_before_offsets"] == Decimal("862.50")
    assert low["issued_before_offsets"] == 862


def test_early_own_claim_does_not_reduce_a_spouse_addon_that_starts_at_fra():
    data = payload()
    data.update(start_year=2026, end_year=2028)
    data["members"][0]["claim_month"] = "2027-01-01"
    data["members"][1]["claim_month"] = "2022-01-01"
    rows = calculate(data)["cash_months"]
    previous = cash_row(dict(cash_months=rows), "spouse", date(2027, 1, 1))
    following = cash_row(dict(cash_months=rows), "spouse", date(2027, 2, 1))
    assert previous["issued_before_offsets"] == 700
    assert following["spousal_excess"] == 250
    assert following["issued_before_offsets"] == 950


def test_uninsured_spouse_can_receive_a_confirmed_spouse_benefit():
    data = payload()
    data["members"][0]["spousal_eligibility_confirmed"] = False
    data["members"][1].update(own_insured=False, pia_january_2026=0)
    row = next(
        r
        for r in calculate(data)["cash_months"]
        if r["member"] == "spouse" and r["issued_before_offsets"]
    )
    assert row["own_with_delayed_credits"] == 0
    assert row["issued_before_offsets"] == 1250
