"""Outside federal/NJ basis and at-risk limits remain distinct from cash and loss timing.

A jurisdiction's deduction use cannot silently overwrite the other basis.
Provided reductions and actual available limits remain individually auditable.
"""

from drilling_cases import change, short

from wealthlab.household.calendar import months
from wealthlab.household.funding import Wallet
from wealthlab.products.drilling_household import Ledger


def test_independent_federal_nj_bases_and_ordinary_recapture_are_preserved():
    def configure(data):
        row = data["drilling_plan"]["observations"][0]
        row.update(exit_requested=False)
        row["deductions"][1].update(nj_requested="50000", nj_basis_reduction="50000")

    case = change(short(2), configure)
    ledger, wallet = Ledger(case), Wallet(case)
    periods = list(months(case.start, case.end))
    ledger.after_receipts(wallet, *periods[0])
    assert ledger.bases == dict(federal=20000, nj=40000, at_risk=20000)
    events = ledger.after_receipts(wallet, *periods[1])
    assert sum(e.federal.allowed_nonpassive_partnership_income for e in events) == 20800
    assert sum(e.new_jersey.business.partnership for e in events) == 800
    assert ledger.bases == dict(federal=0, nj=0, at_risk=0)


def test_at_risk_limit_restricts_tax_loss_without_turning_it_into_cash_or_basis():
    def configure(data):
        row = data["drilling_plan"]["observations"][0]
        row.update(exit_requested=False)
        row["deductions"][1]["federal_limits"]["at_risk"] = "10000"

    case = change(short(), configure)
    ledger, wallet = Ledger(case), Wallet(case)
    events = ledger.after_receipts(wallet, *next(months(case.start, case.end)))
    assert sum(e.federal.allowed_nonpassive_partnership_income for e in events) == -20000
    assert wallet.cash == 100000
    assert ledger.bases["federal"] == 20000
    assert ledger.bases["at_risk"] == 20000
