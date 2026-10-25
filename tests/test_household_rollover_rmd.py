"""An actual plan RMD must be satisfied before eligible source assets can roll into an IRA."""

from plan_rollover_rmd_cases import rmd_data, transfer

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_each_plan_needs_its_own_actual_cash_distribution_before_rollover():
    data = rmd_data()
    data["workplace_plan"]["cash_withdrawals"]["direct_rollovers"] = [
        transfer("alpha_transfer", "alpha_two", "2026-02-01"),
        transfer("beta_early", "beta", "2026-02-01"),
        transfer("beta_after_catchup", "beta", "2026-12-01"),
    ]
    rows = project(Scenario.model_validate(data))
    audit = rows[-1]["workplace_rollover_audit"]
    assert [r["funded"] for r in audit] == [100000, 0, 100000]
    assert audit[1]["source_rmd_unresolved"] == 10000
    assert rows[11]["account_balances"]["ira"] == 200000
    assert rows[11]["ira_annual_reconciliation"]["rmd"]["person_a"]["required"] == 0
    assert rows[11]["net_wealth"] == 492000
    assert rows[11]["workplace_rmd_shortfall"] == 0


def test_prior_year_shortfalls_block_rollovers_even_under_an_excise_waiver_assumption():
    data = rmd_data()
    cash = data["workplace_plan"]["cash_withdrawals"]
    cash["rmd"].update(
        automatic_december_catchup=False,
        shortfall_treatment="irs_waiver_allowed_assumption",
        conditional_relief_confirmed=True,
    )
    cash["direct_rollovers"] = [
        transfer("beta_late", "beta", "2027-12-01"),
    ]
    # Pay the new target in cash: satisfying 2027 does not cure the missed 2026 target.
    cash["orders"].append(
        dict(
            id="beta_new_target",
            provenance="illustration",
            source="beta",
            date="2027-12-01",
            amount=11000,
        )
    )
    rows = project(Scenario.model_validate(data))
    audit = rows[-1]["workplace_rollover_audit"][0]
    assert audit["funded"] == 0
    assert audit["source_rmd_unresolved"] == 10000
    assert rows[-1]["workplace_rmd_unresolved_prior"] == 10000
    assert rows[-1]["workplace_rmd_excise_tax"] == 0
    assert rows[-1]["funding_failure"]
