"""Apply a month in documented funding order and report reserve requirements."""

from decimal import Decimal

from wealthlab.household import debts, flows
from wealthlab.household.calendar import fraction, money
from wealthlab.household.funding import Wallet
from wealthlab.household.scenario import Scenario


def month(scenario: Scenario, wallet: Wallet, debt_balances: dict, start, end, fees_owed) -> dict:
    row = dict(date=start.isoformat(), period_end=end.isoformat(), opening_cash=wallet.cash)
    row["income"] = flows.earnings(scenario, start, end)
    wallet.deposit(row["income"])
    row.update(debts.service(scenario, wallet, debt_balances, start, end))
    row.update(flows.fees(scenario, wallet, start, end, fees_owed))
    row.update(flows.spending(scenario, wallet, start, end))
    row.update(flows.contributions(scenario, wallet, start, end))
    row["closing_cash"] = wallet.cash
    row["account_balances"] = dict(wallet.balances)
    row["debt_balances"] = dict(debt_balances)
    row["funding_shortfall"] = row["debt_shortfall"] + sum(
        value for key, value in row.items() if key.endswith("_unfunded")
    )
    demand = (
        row["debt_payment"]
        + row["current_fees_due"]
        + row["funding_shortfall"]
        - row["fees_unfunded"]
    )
    demand += sum(
        row[key] for key in ("essential", "healthcare", "mortgage", "education", "discretionary")
    )
    row["reserve_target"] = money(
        demand / fraction(start, end) * 12 * Decimal(str(scenario.reserve_years))
    )
    return row
