"""Actual share sales preserve basis, holding character, lockups and year attribution."""

from decimal import Decimal as D

from drilling_cases import change, short

from wealthlab.products.drilling_compare import compare


def test_reference_has_real_short_term_gain_and_independent_cash_receipt():
    case = change(
        short(),
        lambda d: d["drilling_plan"]["observations"][0].update(
            reference_price="110", capital_call="0"
        ),
    )
    # Opening capital rather than a same-day contribution supplies the shares.
    data = case.model_dump(mode="json")
    data["accounts"][1]["balance"] = "100000"
    data["accounts"][0]["balance"] = "100000"
    data["drilling_plan"].update(
        opening_cash="100000",
        opening_federal_basis="100000",
        opening_nj_basis="100000",
        opening_at_risk="100000",
    )
    from wealthlab.household.scenario import Scenario

    result = compare(Scenario.model_validate(data))
    row = result["rows"]["liquid_reference"][0]
    assert (row["drilling_exit_cash"], row["annual_tax"]["federal"]["agi"]) == (
        D("110000"),
        D("10000"),
    )
    assert row["tax_event_cash"] == 0
    assert result["outcomes"]["liquid_reference"]["distributions"] == D("110000")


def test_reference_locked_exit_retains_shares_and_reports_product_failure():
    case = change(
        short(), lambda d: d["drilling_plan"]["observations"][0].update(reference_locked=True)
    )
    result = compare(case)
    row = result["rows"]["liquid_reference"][0]
    assert (row["drilling_account_value"], row["drilling_exit_cash"]) == (D("100000"), 0)
    assert (row["drilling_blocked_exit"], row["drilling_product_failure"]) == (True, True)
    assert row["drilling_audit"]["reference_lots"]
    assert not result["outcomes"]["liquid_reference"]["joint_funding_feasible"]
