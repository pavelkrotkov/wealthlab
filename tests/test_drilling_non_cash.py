"""Supplied depreciation/depletion change independent bases and tax income without creating cash."""

from drilling_cases import change, short

from wealthlab.household.calendar import months
from wealthlab.household.funding import Wallet
from wealthlab.products.drilling_example_terms import deduction
from wealthlab.products.drilling_household import Ledger


def test_paid_tangible_pool_and_production_depletion_are_separate_non_cash_deductions():
    def configure(data):
        row = data["drilling_plan"]["observations"][1]
        row["exit_requested"] = False
        depreciation = deduction("depreciation", "depreciation", 2000)
        depreciation.update(nj_requested="1000", nj_basis_reduction="1000")
        depletion = deduction("depletion", "depletion", 500)
        depletion.update(nj_requested="300", nj_basis_reduction="300")
        row["deductions"].extend([depreciation, depletion])

    case = change(short(2), configure)
    ledger, wallet = Ledger(case), Wallet(case)
    periods = list(months(case.start, case.end))
    ledger.after_receipts(wallet, *periods[0])
    events = ledger.after_receipts(wallet, *periods[1])
    assert ledger.bases == dict(federal=18300, nj=19500, at_risk=18300)
    assert ledger.tangible_basis == dict(federal=18000, nj=19000)
    assert sum(e.federal.allowed_nonpassive_partnership_income for e in events) == -1700
    assert sum(e.new_jersey.business.partnership for e in events) == -500
    assert (wallet.cash, wallet.balances["drilling"]) == (100000, 20800)
    assert sum(e.cash_received for e in events) == 0
