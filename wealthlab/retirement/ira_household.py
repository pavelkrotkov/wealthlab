"""Fixed IRA cash arrives on its date; completed annual basis reaches taxes in December.

No return, conversion or withdrawal is chosen by looking at later values.
Only annual reconciliation uses the completed year's amounts. Until that
reconciliation, household income-tax figures omit the IRA's unfinalized tax.
"""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from wealthlab.retirement.distribution_tax import pension_eligible
from wealthlab.retirement.ira_household_compile import compile_years
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.nj_retirement import RetirementEligibility
from wealthlab.tax.projection_inputs import TaxEvent


class Ledger:
    def __init__(self, scenario):
        self.results = compile_years(scenario)
        self.owners = scenario.ira_plan.owners

    def month(self, wallet, start, end):
        result = next(r for r in self.results if r["year"] == start.year)
        apply_balances(result, wallet, start, end)
        orders = [r for r in result["orders"] if start <= r["date"] < end]
        events = withdrawal_events(orders)
        reconciled = end == date(start.year + 1, 1, 1)
        if reconciled:
            events.append(tax_event(result, self.owners))
        summary = summarize(orders, reconciled)
        if reconciled:
            summary["ira_annual_reconciliation"] = result
        return events, summary


def cash_event(row):
    return TaxEvent(
        date=row["date"],
        description=row["id"],
        cash_received=row["paid"],
        federal=FederalIncome(),
        new_jersey=NJIncome(),
    )


def tax_event(result, owners):
    rows = result["orders"]

    def total(key):
        return sum((r[key] for r in rows), Decimal(0))

    context = SimpleNamespace(year=result["year"], owners=owners)
    return TaxEvent(
        date=date(result["year"], 12, 31),
        description="Completed annual IRA reconciliation",
        cash_received=0,
        federal=FederalIncome(
            ira_distributions=total("federal_taxable"),
            retirement_additional_tax=total("additional_tax"),
            deductible_ira_contributions=sum(
                (p["federal_ira_deduction"] for p in result["contribution_owners"]), Decimal(0)
            ),
        ),
        new_jersey=NJIncome(
            pension=total("nj_taxable"),
            retirement=RetirementEligibility(qualified_pension=pension_eligible(context, rows)),
        ),
    )


def apply_balances(result, wallet, start, end):
    for event in result["balance_events"]:
        if start <= event["date"] < end:
            wallet.balances.update(event["balances"])


def summarize(orders, reconciled):
    return dict(
        ira_withdrawal_cash=paid_kind(orders, "withdrawal"),
        ira_conversion_value=paid_kind(orders, "conversion"),
        ira_unfilled_requests=sum((r["unfilled"] for r in orders), Decimal(0)),
        ira_tax_reconciled=reconciled,
    )


def make(scenario):
    if scenario.ira_plan is None:
        return None
    from wealthlab.retirement.workplace_rollover_validation import orders as rollovers

    if scenario.ira_plan.contributions is not None or rollovers(scenario):
        from wealthlab.retirement.ira_household_dynamic import Ledger as DynamicLedger

        return DynamicLedger(scenario)
    return Ledger(scenario)


def month(ledger, wallet, start, end):
    return ledger.month(wallet, start, end) if ledger else ((), {})


def paid_kind(orders, kind):
    return sum((r["paid"] for r in orders if r["kind"] == kind), Decimal(0))


def withdrawal_events(orders):
    return [cash_event(r) for r in orders if r["kind"] == "withdrawal"]


def receipt_hook(ledger):
    return getattr(ledger, "after_receipts", None)


def completed(ledger, taxes, end):
    if receipt_hook(ledger) is not None:
        return ledger.completed(taxes, end)
    return {}
