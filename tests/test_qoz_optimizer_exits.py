"""An actual stock sale and settlement, not zero shareholder NAV, prove QOF closure."""

import pytest
from qoz_cases import flat

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.optimization.qoz_exits import completed


@pytest.fixture(scope="module")
def closed():
    household = flat()
    return household, project(household)[-1]


def test_actual_taxed_sale_closes_basis_and_receives_cash_once(closed):
    household, row = closed
    assert completed(household, row)
    state = row["qoz_audit"]["economic_state"]
    assert state == dict(sold=True, receivable=0, settlement=None)
    assert row["qoz_settlement_cash"] == 80000
    assert all(
        b["basis"] == 0
        for t in row["qoz_audit"]["tranches"]
        for b in t["tax"]["jurisdictions"].values()
    )


def test_genuine_pending_cash_cannot_be_spendable_exit_wealth():
    data = flat().model_dump(mode="json")
    data["qoz_plan"]["settlement_months"] = 2
    household = Scenario.model_validate(data)
    row = project(household)[-1]
    assert row["qoz_receivable"] == 80000
    row["account_balances"]["qoz"] = 0
    assert not completed(household, row)
