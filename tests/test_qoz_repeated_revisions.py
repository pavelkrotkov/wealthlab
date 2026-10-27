"""Later elections replace only outstanding refund positions, retaining prior receipts."""

from datetime import date
from decimal import Decimal

from qoz_transition_cases import transition

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_second_call_after_first_refund_does_not_pay_that_refund_twice():
    data = transition().model_dump(mode="json")
    call = data["qoz_plan"]["calls"][0]
    call["amount"] = "40000"
    data["qoz_plan"]["calls"].append(dict(call, id="later_call", date="2027-05-31"))
    rows = project(Scenario.model_validate(data))
    first, second = rows[-1]["qoz_audit"]["source_return_revisions"]
    assert first["refund_scheduled"]["date"] == date(2027, 4, 1)
    assert second["refund_scheduled"]["date"] == date(2027, 6, 1)
    actual_first_refund = rows[15]["tax_refund_received"]
    assert (
        sum(second["actual_net_paid"].values())
        == rows[11]["tax_settlement_paid"] - actual_first_refund
    )
    assert sum(r["tax_refund_received"] for r in rows) == rows[11]["tax_settlement_paid"]
    assert rows[-1]["closing_cash"] == Decimal(25000)
    assert rows[-1]["qoz_nav"] == Decimal(80000)
