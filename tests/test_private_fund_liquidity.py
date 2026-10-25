"""Settlement claims preserve wealth while contract locks restrict actual spending cash."""

from private_fund_cases import fund, request

from wealthlab.household.projection import project


def test_notice_lock_quarterly_gate_and_settlement_do_not_create_spendable_cash():
    case = fund(
        requests=[request(40000)],
        lock_until="2026-04-01",
        dealing="quarterly",
        notice_days=60,
        gate_fraction=".25",
        settlement_days=1,
    )
    rows = project(case)
    audit = rows[-1]["sleeve_audit"]
    assert all(r["sleeve_redemptions"] == 0 for r in rows[:6])
    assert audit[5]["fund_receivable"] == 25000
    assert rows[5]["account_balances"]["sleeve"] == 100000
    assert rows[6]["sleeve_redemptions"] == 25000
    assert rows[9]["sleeve_redemptions"] == 15000
    assert all(r["net_wealth"] == 110000 for r in rows)
    assert rows[-1]["closing_cash"] == 50000


def test_unsettled_terminal_proceeds_remain_assets_but_block_complete_exit():
    rows = project(fund(requests=[request(final=True, notice="2026-12-01")], settlement_days=1))
    row = rows[-1]
    assert row["closing_cash"] == 10000
    assert row["account_balances"]["sleeve"] == 100000
    assert row["sleeve_exit_blocked"]
    assert row["sleeve_audit"][-1]["fund_receivable"] == 100000
    assert not row["sleeve_audit"][-1]["fund_complete_liquidation"]
