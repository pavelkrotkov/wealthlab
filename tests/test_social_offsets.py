"""The recipient's delayed credits absorb the extra spouse benefit under SSA dual entitlement.

The relationship eligibility assumption controls whether an auxiliary amount
can exist. It never erases the worker's own delayed retirement benefit.
"""

from datetime import date
from decimal import Decimal

from tests.test_social_cash import calculate, cash_row, payload
from wealthlab.retirement.social import run
from wealthlab.retirement.social_example import synthetic


def test_claimant_delayed_credits_reduce_the_spouse_addon_not_the_own_benefit():
    result = run(synthetic())
    row = cash_row(result, "spouse", date(2031, 1, 1))
    assert row["own_with_delayed_credits"] == 1240
    assert row["spousal_excess"] == 10
    assert row["issued_before_offsets"] == 1250
    annual = next(r for r in result["annual_cash"] if r["year"] == 2031 and r["member"] == "spouse")
    assert annual["issued_before_offsets"] == 15000


def test_denied_spousal_eligibility_leaves_only_own_delayed_benefit():
    data = payload()
    data["members"][1]["spousal_eligibility_confirmed"] = False
    row = next(
        r
        for r in calculate(data)["cash_months"]
        if r["member"] == "spouse" and r["own_with_delayed_credits"]
    )
    assert row["issued_before_offsets"] == 1240
    assert row["spousal_excess"] == Decimal(0)
