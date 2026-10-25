"""Partnership basis allocation remains independent of direct purchase cost.

Federal and NJ property allocations can differ; buying shares after a direct sale
always establishes actual purchase-cost basis instead of adopting those weights.
"""

from exchange_fund_cases import change, flat

from wealthlab.household.projection import project
from wealthlab.products.exchange_fund_household import Ledger


def test_independent_partnership_bases_survive_basket_release_without_forced_sale():
    def configure(data):
        plan = data["exchange_fund_plan"]
        plan["requests"] = plan["requests"][:1]
        plan["basket"][0].update(federal_basis_weight=".7", nj_basis_weight=".2")
        plan["basket"][1].update(federal_basis_weight=".3", nj_basis_weight=".8")

    case = change(flat(), configure)
    audit = project(case)[-1]["exchange_fund_audit"]
    lots = audit["remaining_lots"]
    assert [(lot["federal_basis"], lot["nj_basis"]) for lot in lots] == [
        ("14000.00", "6000.00"),
        ("6000.00", "24000.00"),
    ]
    direct = case.model_copy(
        update={
            "exchange_fund_plan": case.exchange_fund_plan.model_copy(update={"mode": "direct_sale"})
        }
    )
    assert [(lot.federal_basis, lot.nj_basis) for lot in Ledger(direct).book.lots.values()] == [
        (50000, 50000),
        (50000, 50000),
    ]


def test_actual_partial_direct_loss_sale_adjusts_retained_original_wash_basis():
    def configure(data):
        plan = data["exchange_fund_plan"]
        plan.update(mode="direct_sale", contribution_quantity="400")
        plan["source_lot"].update(
            acquired="2025-12-20",
            federal_holding_start="2025-12-20",
            federal_basis="150000",
            nj_basis="90000",
        )

    ledger = Ledger(change(flat(), configure))
    retained = [lot for lot in ledger.book.lots.values() if lot.security_id == "original"]
    assert sum(lot.quantity for lot in retained) == 600
    assert sum(lot.federal_basis for lot in retained) == 110000
    assert sum(lot.nj_basis for lot in retained) == 54000
    assert ledger.opening_events[0].federal.short_term == 0
    assert ledger.opening_events[0].new_jersey.dispositions == 4000
