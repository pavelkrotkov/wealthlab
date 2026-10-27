"""Zero marks cannot certify an unsold property, creditor or deferred tax exit."""

from drilling_cases import change, short

from wealthlab.household.projection import project


def terminal(case):
    return project(case)[-1]["drilling_audit"]


def test_actual_sale_exposes_closed_property_and_independent_zero_balances():
    audit = terminal(short())
    state = audit["terminal_state"]
    assert (state["closed"], state["property_sold"]) == (True, True)
    assert (state["cash"], state["property_value"], state["call_owed"]) == (0, 0, 0)
    assert all(amount == 0 for amount in state["creditors"].values())
    assert all(amount == 0 for amount in state["basis"].values())
    assert state["tangible_basis"] == {"federal": 0, "nj": 0}
    assert audit["future_tax_events"] == []


def test_zero_property_mark_without_executed_sale_still_exposes_unclosed_interest():
    def edit(data):
        data["drilling_plan"]["observations"][0].update(
            residual_property_value="0", exit_requested=False, exit_gross_proceeds="0"
        )

    state = terminal(change(short(), edit))["terminal_state"]
    assert state["property_value"] == 0
    assert (state["closed"], state["property_sold"]) == (False, False)


def test_blocked_sale_retains_each_actual_creditor_and_unsold_property():
    def edit(data):
        data["drilling_plan"]["household_recourse_for_modeled_creditors"] = False
        data["drilling_plan"]["observations"][0]["liability_cost"] = "100000"

    state = terminal(change(short(), edit))["terminal_state"]
    assert (state["closed"], state["property_sold"]) == (False, False)
    assert state["creditors"] == dict(
        operating_cost=0,
        manager_fee=0,
        liability_cost=10000,
        idc_cost=70000,
        tangible_cost=20000,
        exit_cost=0,
    )
    assert state["property_value"] == 20000
