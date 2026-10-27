"""Full exit preserves ordinary recapture and independent jurisdiction signs."""

from drilling_cases import change, short

from wealthlab.household.calendar import months
from wealthlab.household.funding import Wallet
from wealthlab.products.drilling_household import Ledger


def execute(case):
    ledger, wallet = Ledger(case), Wallet(case)
    events = ledger.after_receipts(wallet, *next(months(case.start, case.end)))
    return ledger, events


def test_supplied_recapture_cap_leaves_residual_capital_in_its_own_character():
    case = change(short(), lambda d: d["drilling_plan"].update(federal_recapture_limit="10000"))
    ledger, events = execute(case)
    assert ledger.log[0]["federal_ordinary_recapture"] == 10000
    assert sum(e.federal.allowed_nonpassive_partnership_income for e in events) == -70000
    assert sum(e.federal.short_term for e in events) == 10000
    assert sum(e.federal.long_term for e in events) == 0


def test_federal_positive_recapture_survives_a_denied_nj_exit_loss():
    def configure(data):
        item = data["drilling_plan"]["observations"][0]["deductions"][1]
        item.update(nj_requested="0", nj_basis_reduction="0")

    ledger, events = execute(change(short(), configure))
    assert (ledger.log[0]["federal_exit_gain"], ledger.log[0]["nj_exit_gain"]) == (20000, -50000)
    assert ledger.log[0]["federal_ordinary_recapture"] == 20000
    assert sum(e.federal.allowed_nonpassive_partnership_income for e in events) == -60000
    assert sum(e.federal.short_term for e in events) == 0
    assert sum(e.new_jersey.business.partnership for e in events) == -10000
