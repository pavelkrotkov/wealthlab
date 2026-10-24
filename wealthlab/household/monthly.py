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
from wealthlab.portfolio import household_book
from wealthlab.products import household as sleeves
from wealthlab.retirement import (
    education_household,
    hsa_household,
    ira_household,
    medicare_household,
    workplace,
)
from wealthlab.retirement.household_receipts import receipt_hook
from wealthlab.tax.payments import missed_schedule


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
    ira=None,
    hsa=None,
    education=None,
    lots=None,
    products=None,
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
        quote = (lambda: required_cash + education.cash_need) if education else required_cash
        row.update(
            tax_ledger.month(
                taxable,
                wallet,
                start,
                end,
                quote,
                [*extra_events, *employee_events],
                receipt_hook=receipt_hook(ira, hsa, education, products),
                pre_receipt_hook=lots.after_receipts if lots is not None else None,
            )
        )
        row.update(tax_ledger.close(wallet, start, end))
        row.update(ira_household.completed(ira, tax_ledger, end))
        row.update(hsa_household.completed(hsa, end))
        education_household.completed(education, tax_ledger, end)
        row.update(household_book.completed(lots))
        row.update(sleeves.completed(products))
    row.update(debts.service(scenario, wallet, debt_balances, start, end))
    row.update(flows.fees(scenario, wallet, start, end, fees_owed))
    row.update(flows.spending(scenario, wallet, start, end, medicare, education))
    row.update(flows.contributions(scenario, wallet, start, end))
    row["closing_cash"] = wallet.cash
    row["account_balances"] = dict(wallet.balances)
    row["debt_balances"] = dict(debt_balances)
    return metrics(scenario, row, start, end)


def metrics(scenario, row, start, end):
    row["funding_shortfall"] = row["debt_shortfall"] + sum(
        value for key, value in row.items() if key.endswith("_unfunded")
    )
    row["funding_failure"] = (
        row["funding_shortfall"] > 0 or missed_schedule(row) or row.get("sleeve_failure", False)
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
