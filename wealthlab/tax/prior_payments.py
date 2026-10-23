"""Prior assessed taxes retain jurisdiction when paid in a later calendar year."""

from decimal import Decimal

from wealthlab.tax import state_deduction


def pay(ledger, wallet) -> Decimal:
    total = Decimal(0)
    for jurisdiction in ("new_jersey", "federal"):
        amount = wallet.pay(ledger.outstanding[jurisdiction])
        ledger.outstanding[jurisdiction] -= amount
        total += amount
        if jurisdiction == "new_jersey":
            ledger.case = state_deduction.add(ledger.case, amount, ledger.plan.state_deduction_mode)
    return total


def receive(ledger, wallet, end) -> tuple[Decimal, Decimal]:
    due = [item for item in ledger.refunds if item["date"] < end]
    ledger.refunds = [item for item in ledger.refunds if item["date"] >= end]
    cash = sum((item["cash"] for item in due), Decimal(0))
    taxable = sum((item["taxable"] for item in due), Decimal(0))
    wallet.deposit(cash)
    income = ledger.case.federal_income
    income = income.model_copy(
        update={"taxable_state_refund": income.taxable_state_refund + taxable}
    )
    ledger.case = ledger.case.model_copy(update={"federal_income": income})
    return cash, taxable
