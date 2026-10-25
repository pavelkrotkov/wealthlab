"""Conditional denied and deferred treatments enter actual annual household taxes.

Economic exits and taxable recognition need not occur in the same month.
Deferred losses keep their original supplied basis adjustment and release date;
final K-1 allocations cannot disappear when a fund no longer owns assets.
"""

from exchange_fund_cases import change, flat

from wealthlab.household.projection import project


def test_independent_denied_contribution_and_distribution_are_taxable_without_extra_cash():
    def configure(data):
        plan = data["exchange_fund_plan"]
        plan.update(federal_contribution="denied", nj_basket_distribution="denied")

    rows = project(change(flat(), configure))
    audit = rows[-1]["exchange_fund_audit"]
    contribution = audit["opening_contribution_events"][0]
    assert contribution["federal"]["long_term"] == "80000.00"
    assert contribution["new_jersey"]["dispositions"] == "0"
    assert sum(d["federal_gross_gain"] for d in audit["disposals"]) == 0
    assert sum(d["nj_gross_gain"] for d in audit["disposals"]) == 0
    assert rows[-1]["annual_tax"]["new_jersey"]["gross_income"] == 70000


def test_final_non_cash_allocation_is_recognized_after_earlier_basket_exit():
    from datetime import date

    from wealthlab.products.exchange_fund_example import request

    def configure(data):
        plan = data["exchange_fund_plan"]
        plan.update(
            liquid_after="2026-01-01",
            requests=[
                request("release", date(2026, 1, 31), "redeem"),
                request("sell", date(2026, 1, 31), "sell_liquid"),
            ],
        )
        plan["observations"][-1]["allocation"]["federal"] = dict(interest="500")
        plan["observations"][-1]["allocation"]["new_jersey"] = dict(interest="500")

    rows = project(change(flat(), configure))
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 80500
    assert sum(r["tax_event_cash"] for r in rows) == 0


def test_deferred_supplied_loss_is_recognized_on_its_release_date_once():
    def configure(data):
        mark = data["exchange_fund_plan"]["observations"][0]
        mark["federal_basis_adjustment"] = "-1000"
        mark["allocation"]["federal"] = dict(long_term="-1000")
        mark["allocation"]["federal_loss"] = dict(
            treatment="deferred", release_on="2026-12-31", eligibility_after_limits_assumed=True
        )

    rows = project(change(flat(), configure))
    audit = rows[-1]["exchange_fund_audit"]
    assert sum(d["federal_gross_gain"] for d in audit["disposals"]) == 81000
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 80000
    assert audit["unrecognized_future_events"] == []
