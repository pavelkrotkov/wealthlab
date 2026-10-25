"""A locked plan fails its own requirement; another plan's excess cannot cure it.

With $10,000 beta RMD blocked, ordinary25% excise is $2,500. Alpha already
withheld $2,000, so only another $500 leaves household cash. Reduced/waived
outcomes are explicitly conditional assumptions, never an inferred exemption.
Prior missed requirements remain unresolved after the year changes.
"""

from decimal import Decimal

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace_rmd_example import synthetic


def locked(treatment="ordinary_25_percent"):
    data = synthetic().model_dump(mode="json")
    plan = data["workplace_plan"]
    plan["liquidity_locks"] = [
        dict(
            id="beta_locked",
            provenance="illustration",
            account_id="beta",
            start="2026-12-01",
            end="2027-01-01",
        )
    ]
    plan["cash_withdrawals"]["rmd"].update(
        shortfall_treatment=treatment, conditional_relief_confirmed=True
    )
    return Scenario.model_validate(data)


@pytest.fixture(
    scope="module",
    params=[
        ("ordinary_25_percent", 2500),
        ("timely_correction_10_percent_assumption", 1000),
        ("irs_waiver_allowed_assumption", 0),
    ],
)
def shortfall_case(request):
    treatment, excise = request.param
    return project(locked(treatment)), excise


def test_source_specific_shortfall_and_conditional_tax_enter_wealth_once(shortfall_case):
    rows, excise = shortfall_case
    december = rows[11]
    assert december["workplace_rmd_shortfall"] == 10000
    assert december["workplace_rmd_excise_tax"] == excise
    assert december["annual_tax"]["total_liability"] == excise
    assert december["funding_failure"]
    assert december["net_wealth"] == 492000 - excise
    assert december["account_balances"]["beta"] == 246000


def test_prior_missed_requirement_remains_a_funding_failure(shortfall_case):
    rows, _ = shortfall_case
    assert rows[12]["workplace_rmd_unresolved_prior"] == 10000
    assert rows[12]["funding_failure"]


def test_tax_payment_and_later_plan_target_do_not_rewrite_the_missed_year():
    rows = project(locked())
    assert rows[11]["tax_settlement_paid"] == 500
    assert rows[11]["tax_source_withholding"] == 0
    assert rows[11]["closing_cash"] == 12500
    assert rows[15]["tax_refund_received"] == 0
    assert rows[-1]["workplace_rmd_audit"][1]["shortfall"] == 10000
    assert rows[-1]["workplace_rmd_audit"][3]["required"] == Decimal("10379.75")
    assert rows[-1]["workplace_rmd_unresolved_prior"] == 10000
