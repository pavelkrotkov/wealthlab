"""FRA-year earned wage cutoff uses its distinct frozen threshold and floor-dollar charge."""

from decimal import Decimal as D

from social_work_cases import payload

from wealthlab.retirement.social_work_case import SocialWorkCase
from wealthlab.retirement.social_work_rules import annual_deduction, monthly_exempt


def test_fra_year_uses_only_earned_wages_before_fra_month():
    data = payload()
    data["claims"]["members"][0].update(birth_date="1960-07-02", claim_month="2026-01-01")
    person = SocialWorkCase.model_validate(data).claims.members[0]
    wages = [D(11000)] * 6 + [D(100000)] * 6
    assert annual_deduction(person, 2027, wages) == 280
    assert monthly_exempt(person, 2027) == 5430
    assert annual_deduction(person, 2028, wages) == 0
    wages[5] += D("2.99")
    assert annual_deduction(person, 2027, wages) == 280
