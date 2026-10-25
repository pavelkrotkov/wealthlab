"""Equal opening cash cannot create free policy capital, protection or premium basis."""

from wealthlab.household.projection import project
from wealthlab.products.life_allocation_example import synthetic


def test_zero_opening_new_issue_and_uninsured_reference_preserve_the_same_capital():
    case = synthetic()
    reference, policy = case.alternatives.values()
    assert tuple(sum(a.balance for a in s.accounts) for s in (reference, policy)) == (10000, 10000)
    h = policy.life_plan.holdings[0]
    assert (
        h.contract.opening_federal_basis,
        h.contract.opening_loan,
        h.opening_values.gross_cash_value,
        h.opening_values.gross_surrender_value,
        h.opening_values.gross_death_benefit,
    ) == (0, 0, 0, 0, 0)


def test_uninsured_path_retains_independent_need_without_policy_receipts_or_coverage():
    rows = project(synthetic().alternatives["no_policy"])
    assert [r["closing_cash"] for r in rows] == [9000, 8000, 7000]
    assert [
        (
            r["life_protection_shortfall"],
            r["life_net_death_benefit"],
            r["life_premiums_paid"],
            r["life_reserve_target"],
            r["life_policy_values"],
        )
        for r in rows
    ] == [(150000, 0, 0, 0, [])] * 3
    assert rows[-1]["life_policy_audit"]["executed"] == []
    assert rows[-1]["life_policy_audit"]["inputs"]["holdings"] == []


def test_actual_premiums_build_basis_and_supplied_terminal_cash_is_taxed_once():
    rows = project(synthetic().alternatives["new_issue"])
    assert [r["closing_cash"] for r in rows] == [8000, 6000, 7100]
    assert [r["life_net_death_benefit"] for r in rows] == [100000, 100000, 0]
    assert [r["life_protection_shortfall"] for r in rows] == [50000, 50000, 150000]
    events = rows[-1]["life_policy_audit"]["executed"]
    assert [e["federal_basis_after"] for e in events] == [1000, 2000, 0]
    assert [e["payment_paid"] for e in events] == [1000, 1000, 0]
    assert (
        events[-1]["received_cash"],
        events[-1]["federal_ordinary_income"],
        events[-1]["nj_ordinary_income"],
    ) == (2100, 100, 100)
    assert (
        rows[-1]["annual_tax"]["federal"]["agi"],
        rows[-1]["annual_tax"]["new_jersey"]["gross_income"],
    ) == (100, 100)
