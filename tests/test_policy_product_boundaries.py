"""Zero marked value does not discharge real debt, tax recognition or contractual interests.

The native deferred-recognition cases execute their cash exits but retain real
future tax events. A delayed private-fund settlement remains a claim instead
of cash. These paths must remain ineligible even if marked wealth is high.
"""

from copy import deepcopy

import pytest
from optimization_cases import changed
from optimization_product_cases import case

from wealthlab.markets.paths import generate
from wealthlab.optimization.product_exits import complete
from wealthlab.optimization.search import evaluate


def execute(profile):
    return evaluate(profile, [profile.dimensions[0].choices[0]], 0, generate(profile.training))


@pytest.fixture(scope="module")
def native():
    return execute(case())[1]


@pytest.mark.parametrize("product", ["margin_sleeve", "private_fund", "exchange"])
def test_real_cash_exit_cannot_hide_deferred_tax_beyond_the_horizon(product):
    def edit(data):
        household = data["household"]
        timing = dict(
            treatment="deferred", release_on="2028-01-01", eligibility_after_limits_assumed=True
        )
        if product == "private_fund":
            contract = household["sleeve_plan"]["sleeves"][1]["private_fund_contract"]
            contract.update(federal_opening_basis="11000", federal_exit_loss=timing)
            return
        allocation = dict(
            id="deferred",
            provenance="illustration",
            date="2027-12-31",
            federal=dict(short_term="-1000"),
            new_jersey={},
            federal_loss=timing,
        )
        if product == "exchange":
            household["exchange_fund_plan"]["observations"][-1]["allocation"] = allocation
        else:
            household["sleeve_plan"]["sleeves"][0]["allocations"] = [allocation]

    candidate, result = execute(changed(case(), edit))
    assert result is not None, candidate
    assert result["details"][0]["rows"][-1]["account_balances"][product] == 0
    assert not candidate["constraints"]["completed_after_tax_exit"]
    assert candidate["median_real_after_tax_exit_wealth"] is None


def test_unsettled_private_redemption_is_a_claim_and_never_cash_or_completed_exit():
    profile = changed(
        case(),
        lambda d: d["household"]["sleeve_plan"]["sleeves"][1]["private_fund_contract"]["requests"][
            0
        ].update(notice_date="2027-09-01"),
    )
    candidate, result = execute(profile)
    row = result["details"][0]["rows"][-1]
    assert row["account_balances"]["private_fund"] == 10000
    assert row["closing_cash"] == 281999
    assert not candidate["eligible"]


def test_zero_nav_active_exchange_interest_remains_open(native):
    row = deepcopy(native["details"][0]["rows"][-1])
    row["exchange_fund_audit"]["terminal_state"]["active"] = True
    assert row["account_balances"]["exchange"] == 0
    assert not complete(case().household, row)
