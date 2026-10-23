"""Contractual debt payments, with unpaid interest retained as an obligation."""

from decimal import Decimal

from wealthlab.household.calendar import fraction, money
from wealthlab.household.funding import Wallet
from wealthlab.household.scenario import Scenario


def opening_debts(scenario: Scenario) -> dict[str, Decimal]:
    return {
        debt.id: money(debt.balance * Decimal(str(scenario.usd_per_currency[debt.currency])))
        for debt in scenario.debts
    }


def service(scenario: Scenario, wallet: Wallet, balances: dict, start, end) -> dict:
    totals = dict(
        interest=Decimal(0),
        interest_paid=Decimal(0),
        principal=Decimal(0),
        debt_payment=Decimal(0),
        debt_shortfall=Decimal(0),
    )
    for debt in scenario.debts:
        interest, due = payment(debt, balances[debt.id], scenario, start, end)
        paid = wallet.pay(due)
        balances[debt.id] += interest - paid
        totals["interest"] += interest
        totals["interest_paid"] += min(paid, interest)
        totals["principal"] += max(Decimal(0), paid - interest)
        totals["debt_payment"] += paid
        totals["debt_shortfall"] += due - paid
    return totals


def payment(debt, opening: Decimal, scenario: Scenario, start, end) -> tuple[Decimal, Decimal]:
    interest = money(opening * Decimal(str(debt.annual_rate)) / 12 * fraction(start, end))
    scheduled = money(
        debt.monthly_payment
        * Decimal(str(scenario.usd_per_currency[debt.currency]))
        * fraction(start, end)
    )
    return interest, min(opening + interest, scheduled)
