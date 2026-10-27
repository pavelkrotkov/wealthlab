"""Carried capital-call obligations can create replacement buys within a wash window."""

from drilling_cases import change, short

from wealthlab.household.calendar import months
from wealthlab.household.funding import Wallet
from wealthlab.products.drilling_household import Ledger


def test_unfunded_call_keeps_actual_loss_pending_until_future_funding_and_disposal():
    def edit(data):
        data["accounts"][0]["balance"] = "0"
        data["accounts"][1]["balance"] = "100000"
        plan = data["drilling_plan"]
        plan.update(
            mode="liquid_reference",
            opening_cash="100000",
            opening_federal_basis="100000",
            opening_nj_basis="100000",
            opening_at_risk="100000",
        )
        first, last = plan["observations"]
        first.update(reference_price="90", reference_cash_request="90000")
        last["reference_price"] = "90"

    case = change(short(2), edit)
    ledger, wallet = Ledger(case), Wallet(case)
    first, last = months(case.start, case.end)
    before = ledger.after_receipts(wallet, *first)
    assert (before[-1].federal.short_term, ledger.call_owed) == (0, 100000)
    assert ledger.reference_book.disposals[0]["federal_pending_loss"] == 10000
    after = ledger.after_receipts(wallet, *last)
    assert (after[-1].federal.short_term, ledger.call_owed) == (-10000, 10000)
    assert wallet.cash == 90000
