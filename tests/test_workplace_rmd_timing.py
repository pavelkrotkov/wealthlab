"""Current targets are fixed before new-year deposits/returns; future targets use actual assets.

The alpha plan pays $15,000 before a10% gain on its remaining $108,000
subaccount. Its current requirement stays $10,000; next year's base becomes
$241,800 and divides by23.7, rounded upward to $10,202.54.
"""

from datetime import date
from decimal import Decimal

from wealthlab.household.funding import Wallet
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace import Ledger
from wealthlab.retirement.workplace_rmd_example import synthetic


def test_current_target_ignores_later_cash_transfers_into_a_plan():
    scenario = synthetic()
    ledger, wallet = Ledger(scenario), Wallet(scenario)
    ledger.rmd.start(wallet, date(2026, 1, 1))
    wallet.balances["alpha_one"] += Decimal(24600)
    ledger.rmd.start(wallet, date(2026, 2, 1))
    assert ledger.rmd.current["alpha"]["required"] == 10000
    assert ledger.rmd.current["alpha"]["prior_december_balances"]["alpha_one"] == 123000


def test_current_requirement_stays_fixed_and_next_year_uses_actual_marked_assets():
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["returns"] = [
        dict(
            id="gain",
            provenance="illustration",
            date="2026-03-31",
            account_id="alpha_one",
            rate=".10",
        )
    ]
    rows = project(Scenario.model_validate(data))
    audit = rows[-1]["workplace_rmd_audit"]
    assert audit[0]["required"] == 10000
    assert audit[2]["required"] == Decimal("10202.54")
    assert rows[-1]["net_wealth"] == 502800


def test_zero_balance_plan_has_no_phantom_requirement_or_auto_withdrawal():
    data = synthetic().model_dump(mode="json")
    data["accounts"][3]["balance"] = 0
    rows = project(Scenario.model_validate(data))
    assert rows[11]["workplace_rmd_required"] == 10000
    assert rows[11]["workplace_withdrawal_gross"] == 0
    assert rows[-1]["workplace_rmd_audit"][1]["required"] == 0
    assert rows[-1]["net_wealth"] == 246000


def test_empty_manual_schedule_can_use_explicit_automatic_rmd_funding():
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["cash_withdrawals"]["orders"] = []
    rows = project(Scenario.model_validate(data))
    assert rows[1]["workplace_withdrawal_gross"] == 0
    assert rows[11]["workplace_withdrawal_gross"] == 20000
    assert rows[11]["tax_source_withholding"] == 2000
    assert rows[-1]["net_wealth"] == 492000
