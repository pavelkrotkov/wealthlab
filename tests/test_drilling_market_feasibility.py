"""Required product obligations remain failures even when ordinary bills are paid.

The zero-wallet case owes one $100,000 creditor balance, although the native
call and creditor diagnostics both show that amount. A locked liquid reference
still owns $100,000 shares. The solvent well spends $60,000 and returns $40,000
of its $100,000 call, leaving $140,000 from $200,000 original household capital.
These independent cash identities stay separate from the feasibility verdict.
"""

from drilling_cases import change, short

from wealthlab.household.projection import project
from wealthlab.markets.household_outcomes import funding
from wealthlab.products.drilling_compare import compare


def test_unpaid_call_and_creditors_fail_joint_safety_without_double_counting_wealth():
    def configure(data):
        data["accounts"][0]["balance"] = "0"
        data["drilling_plan"]["observations"][0].update(
            residual_property_value="0", exit_gross_proceeds="0"
        )

    rows = project(change(short(), configure))
    result = funding(rows)
    assert rows[0]["drilling_call_owed"] == rows[0]["drilling_creditor_payables"] == 100000
    assert rows[0]["net_wealth"] == -100000
    assert result["funded"]
    assert not result["joint_feasible"]
    assert not result["drilling_feasible"]
    assert result["product_constraints_failed_months"] == result["drilling_failure_months"] == 1
    assert result["first_product_failure"] == result["first_drilling_failure"] == "2026-01-01"


def test_locked_liquid_reference_also_fails_the_same_generic_product_constraint():
    case = change(
        short(), lambda d: d["drilling_plan"]["observations"][0].update(reference_locked=True)
    )
    rows = compare(case)["rows"]["liquid_reference"]
    result = funding(rows)
    assert rows[-1]["drilling_account_value"] == 100000
    assert result["funded"]
    assert not result["joint_feasible"]
    assert result["drilling_failure_months"] == 1


def test_funded_executed_drilling_exit_keeps_joint_feasibility():
    rows = project(short())
    result = funding(rows)
    assert rows[-1]["net_wealth"] == 140000
    assert result["funded"] and result["joint_feasible"] and result["drilling_feasible"]
    assert result["drilling_failure_months"] == 0
    assert result["first_drilling_failure"] is None
