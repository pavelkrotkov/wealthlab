"""Rejected acceptance retains actual shares until sale, without sponsor benefits."""

from exchange_allocation_cases import allocated

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_denied_acceptance_can_execute_a_source_sale_without_creating_fund_assets_or_fees():
    data = allocated(400).model_dump(mode="json")
    data["exchange_fund_plan"].update(accepted=False, annual_fee="1")
    rows = project(Scenario.model_validate(data))
    final = rows[-1]
    audit = final["exchange_fund_audit"]
    assert sum(row["exchange_fees"] for row in rows) == 0
    assert final["exchange_source_sale_cash"] == 100000
    assert audit["opening_contribution_events"] == []
    assert audit["exit_status"]["fund_entered"] is False
    assert audit["exit_status"]["modeled_exit_complete"] is True
    assert final["annual_tax"]["federal"]["agi"] == 80000


def test_unaccepted_unsold_stock_is_not_closed_merely_because_fund_nav_is_zero():
    data = allocated(400, source_sale=False).model_dump(mode="json")
    data["exchange_fund_plan"]["accepted"] = False
    final = project(Scenario.model_validate(data))[-1]
    assert final["exchange_locked_value"] == 0
    assert final["exchange_retained_source_quantity"] == 1000
    assert final["exchange_positions_closed"] is False
    assert final["exchange_fund_audit"]["exit_status"]["modeled_exit_complete"] is False
