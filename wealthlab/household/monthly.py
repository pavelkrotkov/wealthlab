"""Apply the monthly funding order, then report current obligations and reserves.

Premiums join healthcare spending; unpaid bills remain separate liabilities.
Reserve demand excludes payments curing prior Medicare arrears, so paying an
old bill does not falsely increase the current recurring spending target.
"""

from decimal import Decimal

from wealthlab.household import debts, flows, needs
from wealthlab.household.calendar import fraction, money
from wealthlab.household.funding import Wallet
from wealthlab.household.scenario import Scenario
from wealthlab.retirement import medicare_household, workplace


def month(
    scenario: Scenario,
    wallet: Wallet,
    debt_balances: dict,
    start,
    end,
    fees_owed,
    tax_ledger=None,
    extra_events=(),
    medicare=None,
    employee=None,
) -> dict:
    row = dict(date=start.isoformat(), period_end=end.isoformat(), opening_cash=wallet.cash)
    incomes = flows.earning_items(scenario, start, end)
    row["income"] = sum(incomes.values(), Decimal(0))
    wallet.deposit(row["income"])
    taxable, employee_events, contributions = workplace.month(employee, wallet, incomes, start, end)
    row.update(contributions)
    if tax_ledger is not None:
        required_cash = needs.required(scenario, debt_balances, start, end, fees_owed)
        required_cash += medicare_household.required(medicare)
        row.update(
            tax_ledger.month(
                taxable, wallet, start, end, required_cash, [*extra_events, *employee_events]
            )
        )
        row.update(tax_ledger.close(wallet, start, end))
    row.update(debts.service(scenario, wallet, debt_balances, start, end))
    row.update(flows.fees(scenario, wallet, start, end, fees_owed))
    row.update(flows.spending(scenario, wallet, start, end, medicare))
    row.update(flows.contributions(scenario, wallet, start, end))
    row["closing_cash"] = wallet.cash
    row["account_balances"] = dict(wallet.balances)
    row["debt_balances"] = dict(debt_balances)
    return metrics(scenario, row, start, end)


def metrics(scenario, row, start, end):
    row["funding_shortfall"] = row["debt_shortfall"] + sum(
        value for key, value in row.items() if key.endswith("_unfunded")
    )
    row["funding_failure"] = any(
        row.get(key, 0) > 0
        for key in ("funding_shortfall", "tax_payment_gap", "tax_settlement_payment_gap")
    )
    demand = (
        row["debt_payment"]
        + row["current_fees_due"]
        + row["funding_shortfall"]
        - row["fees_unfunded"]
        - row.get("tax_unfunded", Decimal(0))
        - row.get("medicare_arrears_paid", Decimal(0))
    )
    demand += sum(
        row[key] for key in ("essential", "healthcare", "mortgage", "education", "discretionary")
    )
    row["reserve_target"] = money(
        demand / fraction(start, end) * 12 * Decimal(str(scenario.reserve_years))
    )
    row["reserve_target"] += money(
        row.get("tax_annualized_run_rate", Decimal(0)) * Decimal(str(scenario.reserve_years))
    )
    return row
