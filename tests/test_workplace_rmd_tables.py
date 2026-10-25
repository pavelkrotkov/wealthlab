"""Beneficiary tables, source-tax choices and aggregate cent allocation remain explicit."""

from datetime import date

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace_rmd_example import synthetic
from wealthlab.retirement.workplace_rmd_validation import validate


def test_confirmed_sole_younger_spouse_uses_its_own_plan_divisor():
    data = synthetic().model_dump(mode="json")
    group = data["workplace_plan"]["cash_withdrawals"]["rmd"]["groups"]["alpha"]
    group.update(rmd_table="sole_younger_spouse", spouse_birth_date="1965-07-01")
    rows = project(Scenario.model_validate(data))
    alpha, beta = rows[-1]["workplace_rmd_audit"][:2]
    assert alpha["divisor"] > beta["divisor"]
    assert alpha["required"] < beta["required"]
    assert rows[-1]["net_wealth"] == 492000


@pytest.mark.parametrize("born", [None, "1966-07-01", "1956-01-01"])
def test_joint_table_does_not_accept_an_unknown_or_wrong_spouse(born):
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["cash_withdrawals"]["rmd"]["groups"]["alpha"].update(
        rmd_table="sole_younger_spouse", spouse_birth_date=born
    )
    with pytest.raises(ValueError, match="actual sole spouse"):
        validate(Scenario.model_validate(data))


def test_under_age75_owner_has_no_current_rmd_without_guessing_future_start():
    from wealthlab.household.funding import Wallet
    from wealthlab.retirement.workplace import Ledger

    scenario = synthetic()
    ledger = Ledger(scenario)
    for person in ledger.rmd.people.values():
        person.birth_date = date(1960, 7, 1)
    ledger.rmd.start(Wallet(scenario), date(2034, 1, 1))
    assert ledger.rmd.current["alpha"]["required"] == 0
    ledger.rmd.start(Wallet(scenario), date(2035, 1, 1))
    assert ledger.rmd.current["alpha"]["required"] == 10000
