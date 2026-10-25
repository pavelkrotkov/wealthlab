"""Conditional denied and deferred jurisdiction treatments enter actual annual household taxes."""

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
