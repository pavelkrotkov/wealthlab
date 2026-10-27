"""Supplied depreciation/depletion change independent bases and tax income without creating cash."""

from drilling_cases import change, short

from wealthlab.household.calendar import months
from wealthlab.household.funding import Wallet
from wealthlab.products.drilling_example_terms import deduction
from wealthlab.products.drilling_household import Ledger


def test_no_production_cannot_create_a_supplied_depletion_deduction():
    def configure(data):
        row = data["drilling_plan"]["observations"][0]
        row["deductions"].append(deduction("dry_depletion", "depletion", 10000))

    case = change(short(), configure)
    ledger, wallet = Ledger(case), Wallet(case)
    events = ledger.after_receipts(wallet, *next(months(case.start, case.end)))
    assert sum(e.federal.allowed_nonpassive_partnership_income for e in events) == -60000
    entries = [d for d in ledger.log[0]["deduction_audit"] if d["component"] == "depletion"]
    assert all(d["limited_amount"] == 0 for d in entries)
