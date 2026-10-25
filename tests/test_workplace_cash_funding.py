"""Cash limits, locks and cent rounding never create plan assets or recipient cash.

The age-55 exception depends on separation year; waiting to turn 55 cannot
repair an age-54 separation. At exactly 59½ ordinary access independently
removes age-based additional tax, even without the separation exception.
"""

from datetime import date
from decimal import Decimal

import pytest

from wealthlab.household.funding import Wallet
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace import Ledger
from wealthlab.retirement.workplace_withdrawal_example import synthetic
from wealthlab.retirement.workplace_withdrawals import withdraw


@pytest.mark.parametrize(
    "born,separated,additional",
    [
        ("1971-07-01", "2025-12-31", 1000),
        ("1971-07-01", "2026-01-01", 0),
        ("1966-08-01", "2016-01-01", 0),
        ("1966-08-02", "2016-01-01", 1000),
    ],
)
def test_exact_access_age_and_separation_calendar_year(born, separated, additional):
    ledger = Ledger(synthetic())
    ledger.birth_dates["person_a"] = date.fromisoformat(born)
    plan = ledger.plan.cash_withdrawals
    profile = plan.profiles["work_pretax"].model_copy(
        update=dict(separation_date=date.fromisoformat(separated))
    )
    row, event = withdraw(ledger, Wallet(synthetic()), plan.orders[0], profile)
    assert row["additional_tax"] == event.federal.retirement_additional_tax == additional
    assert event.federal.taxable_pension == 10000
    assert event.cash_received == 8000


def test_under_age55_separation_owes_additional_tax_and_refunds_only_excess_credit():
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["cash_withdrawals"]["profiles"]["work_pretax"]["separation_date"] = (
        "2025-12-31"
    )
    rows = project(Scenario.model_validate(data))
    assert rows[1]["workplace_withdrawal_additional_tax"] == 1000
    assert rows[11]["annual_tax"]["total_liability"] == 1000
    assert rows[15]["tax_refund_received"] == 1000
    assert rows[-1]["net_wealth"] == 99000


def test_insufficient_balances_limit_actual_gross_before_withholding():
    scenario = synthetic()
    ledger, wallet = Ledger(scenario), Wallet(scenario)
    order = ledger.plan.cash_withdrawals.orders[0]
    profile = ledger.plan.cash_withdrawals.profiles[order.source]
    wallet.balances[order.source] = Decimal(3000)
    row, event = withdraw(ledger, wallet, order, profile)
    assert row["gross"] == 3000
    assert row["unfilled"] == 7000
    assert event.cash_received == 2400
    assert event.withholding.total == 600
    assert wallet.balances[order.source] == 0
    second, empty = withdraw(ledger, wallet, order, profile)
    assert second["gross"] == empty.cash_received == 0


def test_independent_source_tax_rounding_cannot_make_a_negative_cent_receipt():
    scenario = synthetic()
    ledger, wallet = Ledger(scenario), Wallet(scenario)
    plan = ledger.plan.cash_withdrawals
    order = plan.orders[0].model_copy(
        update=dict(
            amount=Decimal(".03"),
            federal_withholding_rate=Decimal(".5"),
            nj_withholding_rate=Decimal(".5"),
        )
    )
    _, event = withdraw(ledger, wallet, order, plan.profiles[order.source])
    assert event.withholding.total == Decimal(".03")
    assert event.withholding.federal_income_withheld == Decimal(".02")
    assert event.cash_received == 0


def test_actual_account_lock_blocks_gross_net_tax_and_hsa_funding():
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["liquidity_locks"] = [
        dict(
            id="locked",
            provenance="illustration",
            account_id="work_pretax",
            start="2026-02-01",
            end="2026-03-01",
        )
    ]
    rows = project(Scenario.model_validate(data))
    assert rows[1]["workplace_withdrawal_gross"] == 0
    assert rows[1]["workplace_withdrawal_unfilled"] == 10000
    assert rows[1]["hsa_personal_contributions"] == 0
    assert rows[1]["tax_source_withholding"] == 0
    assert rows[-1]["account_balances"]["work_pretax"] == 100000


@pytest.mark.parametrize("born,qualified", [("1971-07-01", 0), ("1964-12-31", 10000)])
def test_nj_pension_exclusion_uses_distributing_owner_age(born, qualified):
    scenario = synthetic()
    ledger = Ledger(scenario)
    ledger.birth_dates["person_a"] = date.fromisoformat(born)
    plan = ledger.plan.cash_withdrawals
    _, event = withdraw(ledger, Wallet(scenario), plan.orders[0], plan.profiles["work_pretax"])
    assert event.new_jersey.retirement.qualified_pension == qualified
