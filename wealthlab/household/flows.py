"""Dated income, spending and transfers in a common USD reporting currency."""

from decimal import Decimal

from wealthlab.household.calendar import amount, fraction, money
from wealthlab.household.funding import Wallet
from wealthlab.household.scenario import Scenario


def earning_items(scenario: Scenario, start, end) -> dict[str, Decimal]:
    retirement = {member.id: member.retirement_date for member in scenario.members}
    result = {}
    for income in scenario.incomes:
        cutoff = min(end, retirement[income.owner]) if income.stop_at_retirement else end
        result[income.id] = amount(income, start, cutoff, scenario)
    return result


def earnings(scenario: Scenario, start, end) -> Decimal:
    return sum(earning_items(scenario, start, end).values(), Decimal(0))


def spending(scenario: Scenario, wallet: Wallet, start, end) -> dict:
    result = {}
    for category in ("essential", "healthcare", "mortgage", "education", "discretionary"):
        due = sum(
            (
                amount(item, start, end, scenario)
                for item in scenario.expenses
                if item.category == category
            ),
            Decimal(0),
        )
        paid = wallet.pay(due)
        result[category] = paid
        result[f"{category}_unfunded"] = due - paid
    return result


def contributions(scenario: Scenario, wallet: Wallet, start, end) -> dict:
    result = dict(contributions=Decimal(0), contributions_skipped=Decimal(0))
    for transfer in scenario.contributions:
        due = amount(transfer, start, end, scenario)
        paid = wallet.pay(due)
        wallet.balances[transfer.destination] += paid
        result["contributions"] += paid
        result["contributions_skipped"] += due - paid
    return result


def fees(scenario: Scenario, wallet: Wallet, start, end, owed: Decimal) -> dict:
    """Pay arrears first, then new fees; retain only the unpaid balance as a liability.

    New shortfalls exclude previously reported arrears to avoid counting the same
    missed payment again in the cumulative funding-failure diagnostic.
    """
    due = fee_due(scenario, start, end)
    paid = wallet.pay(owed + due)
    newly_unfunded = due - max(Decimal(0), paid - owed)
    return dict(
        fees=paid, fees_unfunded=newly_unfunded, fees_owed=owed + due - paid, current_fees_due=due
    )


def fee_due(scenario: Scenario, start, end) -> Decimal:
    return money(
        sum(
            (
                account.monthly_fee * Decimal(str(scenario.usd_per_currency[account.currency]))
                for account in scenario.accounts
            ),
            Decimal(0),
        )
        * fraction(start, end)
    )
