"""Only actual remaining proceeds fund a call; a prospective refund is unavailable."""

from decimal import Decimal

from qoz_transition_cases import transition

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_tax_already_paid_limits_actual_eligible_investment_without_refund_borrowing():
    data = transition().model_dump(mode="json")
    data["accounts"][0]["balance"] = "0"
    data["lot_plan"]["case"]["lots"][0].update(federal_basis="0", nj_basis="0")
    data["qoz_plan"]["calls"][0]["amount"] = "100000"
    rows = project(Scenario.model_validate(data))
    paid = rows[11]["tax_settlement_paid"]
    call = rows[-1]["qoz_audit"]["calls"][0]
    assert paid > 0
    assert call["funded"] == Decimal(100000) - paid
    assert call["elected"]["federal"] == call["funded"]
    assert rows[12]["qoz_call_unfunded"] == paid
    assert rows[12]["closing_cash"] == 0
    assert rows[12]["tax_refund_received"] == 0
