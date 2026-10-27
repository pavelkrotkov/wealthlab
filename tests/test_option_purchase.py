"""New shares must consume actual cash, acquire current basis and unwind actual gross exposure."""

from decimal import Decimal

from wealthlab.household.projection import project
from wealthlab.products.option_book import OptionBook
from wealthlab.products.option_engine import run
from wealthlab.products.option_exit_state import from_rows
from wealthlab.products.option_opening import purchase
from wealthlab.products.option_purchase_example import synthetic, unit_plan
from wealthlab.products.option_stress import stress


def test_new_stock_purchase_assignment_and_tax_basis_reconcile_once():
    case = unit_plan().case
    before = case.model_dump_json()
    result = run(case)
    assert case.model_dump_json() == before
    opening = result["rows"][0]
    assert opening["shares"] == 100
    assert opening["federal_basis"] == opening["nj_basis"] == 10002
    assert opening["cash"] == 2497
    # $12k -100 shares*$100 -$2 buyfee +$500 premium -$1 option fee
    # +100 shares*$110 assignment -$1 delivery fee = $13,496 actual cash.
    assert result["ending"]["cash"] == result["ending"]["wealth"] == 13496
    assert [(t["action"], t["date"]) for t in result["stock_trades"]] == [
        ("buy", "2026-01-01"),
        ("sell", "2026-02-28"),
    ]


def test_new_stock_tax_character_comes_from_actual_acquisition_not_old_lot_history():
    result = run(unit_plan().case)
    federal = next(row for row in result["tax"] if row["jurisdiction"] == "federal")
    assert federal["recognized"] == federal["short_term"] == 1496
    assert federal["long_term"] == 0
    assert result["exit_state"]["modeled_cash_exit_complete"]


def test_new_stock_actual_household_sweep_and_spending_use_same_cash():
    rows = project(synthetic())
    # The account starts with $12k cash, not stock; $1k household cash and
    # $1,496 trading profit less $6k spending leave $8,496 in the real Wallet.
    assert rows[0]["closing_cash"] == 2997
    assert rows[-1]["closing_cash"] == rows[-1]["net_wealth"] == 8496
    exit_state = from_rows(rows)
    assert exit_state["stock_trades"][0]["quantity"] == "100"
    assert exit_state["modeled_cash_exit_complete"]
    assert exit_state["cash"] == exit_state["owned_shares"] == 0
    assert exit_state["settlement_loan"] == exit_state["collateral"] == 0


def test_rejected_opening_purchase_never_moves_partial_reserve_or_account_cash():
    case = unit_plan().case
    account = case.holdings.accounts[0].model_copy(update={"cash": Decimal(100)})
    book = case.holdings.model_copy(update={"accounts": [account]})
    state = OptionBook(case.model_copy(update={"holdings": book, "outside_cash": Decimal(50)}))
    purchase(state, case.marks[0])
    assert state.book.cash[state.account] == 100
    assert state.reserve == 50
    assert state.loan == 0
    assert not state.book.lots and not state.book.history
    assert state.failures == ["new_stock: unfunded opening stock purchase"]


def test_stress_uses_actual_purchased_stock_and_does_not_invent_rejected_shares():
    case = unit_plan().case
    flat = next(row for row in stress(case) if row["stock_shock"] == row["index_shock"] == 0)
    assert flat["stock_value"] == 10000
    assert flat["wealth"] == run(case)["rows"][0]["wealth"]
    account = case.holdings.accounts[0].model_copy(update={"cash": Decimal(1)})
    broken = case.model_copy(
        update={"holdings": case.holdings.model_copy(update={"accounts": [account]})}
    )
    assert all(row["execution_failed"] for row in stress(broken))
    assert all(row["stock_value"] == 0 for row in stress(broken))
