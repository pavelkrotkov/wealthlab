"""Current Part B stays withheld while cash-only health bills can become arrears."""

from datetime import date
from decimal import Decimal

from wealthlab.household.projection import project
from wealthlab.retirement.social_medicare_example import synthetic


def test_spending_stress_after_claim_start_keeps_cash_premiums_and_withholding_distinct():
    case = synthetic()
    shock = case.expenses[0].model_copy(
        update=dict(id="spending_shock", start=date(2030, 3, 1), monthly_amount=Decimal(1000000))
    )
    rows = project(case.model_copy(update=dict(expenses=[*case.expenses, shock])))
    april = rows[3]
    assert (
        april["closing_cash"],
        april["social_security_cash"],
        april["medicare_benefit_withheld"],
        april["medicare_unfunded"],
    ) == (0, 3944, Decimal("405.80"), 480)
    assert (rows[-1]["medicare_owed"], rows[-1]["net_wealth"]) == (16320, 83680)
    assert any(r["funding_failure"] for r in rows)
