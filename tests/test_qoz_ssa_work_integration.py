"""A carried government claim cannot subscribe to a fund before actual receipt.

The synthetic worker owns a $3,372 SSA claim in January 2027 but receives only
$562 current cash. An optional $1,000 normal-cost subscription can invest that
$562, leaving $438 unfilled and the separate $800 spending bill unfunded.
The source stock has no gain, so no QOZ tax election masks the cash constraint.
"""

from qoz_cases import flat
from social_work_household_cases import payload

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def combined():
    data = payload()
    data["accounts"][0]["balance"] = "0"
    data["expenses"][0]["monthly_amount"] = "800"
    data["incomes"], data["tax_plan"]["income_rules"] = [], []
    fund = flat(2026, 2).model_dump(mode="json")
    for account in fund["accounts"][1:]:
        account["owner"] = "worker"
    data["accounts"].extend(fund["accounts"][1:])
    data.update(lot_plan=fund["lot_plan"], qoz_plan=fund["qoz_plan"])
    data["lot_plan"]["case"]["lots"][0].update(federal_basis="100000", nj_basis="100000")
    first = data["qoz_plan"]["calls"][0]
    first["amount"] = "100000"
    data["qoz_plan"]["calls"].append(
        dict(first, id="later_subscription", date="2027-01-31", amount="1000")
    )
    data["qoz_plan"]["prior_source_year_revision_assumed_confirmed"] = True
    return Scenario.model_validate(data)


def test_only_actual_ssa_cash_can_fund_a_qoz_subscription_not_a_government_receivable():
    rows = project(combined())
    january = rows[12]
    assert january["social_security_government_receivable"] == 3372
    assert january["social_security_net_cash"] == 562
    assert january["qoz_call_paid"] == 562
    assert january["qoz_call_unfunded"] == 438
    assert january["closing_cash"] == 0
    assert january["essential_unfunded"] == 800
