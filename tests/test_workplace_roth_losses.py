"""Losses and locks do not create negative income, extra spending cash or a deduction."""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace_roth_example import synthetic


def test_full_cash_exit_after_loss_retains_unrecovered_cost_without_a_tax_savings_receipt():
    data = synthetic().model_dump(mode="json")
    data["accounts"][1]["balance"] = 5000
    plan = data["workplace_plan"]["roth_cash_withdrawals"]
    plan["orders"].append(dict(plan["orders"][0], id="later_draw", date="2027-02-01"))
    rows = project(Scenario.model_validate(data))
    audit = rows[-1]["workplace_roth_audit"]
    contract = rows[-1]["workplace_roth_contracts"][0]
    assert [r["gross"] for r in audit] == [5000, 0]
    assert audit[0]["federal_taxable"] == 0
    assert (contract["value"], contract["federal_basis"], contract["nj_basis"]) == (0, 4400, 4000)
    assert contract["modeled_cash_loss_deduction"] == 0
    assert rows[-1]["net_wealth"] == 5000


def test_temporary_outgoing_lock_does_not_retry_or_consume_cost():
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["liquidity_locks"] = [
        dict(
            id="cash_lock",
            provenance="illustration",
            account_id="work_roth",
            start="2026-02-01",
            end="2026-03-01",
        )
    ]
    rows = project(Scenario.model_validate(data))
    audit = rows[-1]["workplace_roth_audit"]
    assert len(audit) == 1
    assert audit[0]["blocked_by_liquidity"]
    assert audit[0]["gross"] == 0
    assert rows[-1]["workplace_roth_contracts"][0]["federal_basis"] == 9400
    assert rows[-1]["net_wealth"] == 10000
