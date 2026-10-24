"""Monthly cash conservation before the later household tax and market modules."""

from decimal import Decimal

from wealthlab.employment.compensation import Ledger as CompensationLedger
from wealthlab.employment.compensation_projection import prepare as prepare_compensation
from wealthlab.employment.compensation_reporting import snapshot as compensation_snapshot
from wealthlab.employment.wages import prepare as prepare_employment
from wealthlab.household import debts
from wealthlab.household.calendar import money, months
from wealthlab.household.funding import Wallet
from wealthlab.household.monthly import month
from wealthlab.household.scenario import Scenario
from wealthlab.household.validation import validate_resolved
from wealthlab.retirement.social_household import prepare
from wealthlab.tax.projection_ledger import TaxLedger


def project(scenario: Scenario) -> list[dict]:
    scenario = prepare(prepare_compensation(prepare_employment(scenario)))
    validate_resolved(scenario)
    wallet = Wallet(scenario)
    debt_balances = debts.opening_debts(scenario)
    rows, fees_owed = [], Decimal(0)
    tax_ledger = TaxLedger(scenario.tax_plan, scenario) if scenario.tax_plan else None
    compensation = CompensationLedger(scenario) if scenario.compensation_plan else None
    for start, end in months(scenario.start, scenario.end):
        events = compensation.month(wallet, start, end) if compensation else ()
        row = month(scenario, wallet, debt_balances, start, end, fees_owed, tax_ledger, events)
        if compensation:
            row.update(compensation_snapshot(compensation, wallet, end))
        fees_owed = row["fees_owed"]
        row["net_wealth"] = sum(wallet.balances.values()) - sum(debt_balances.values()) - fees_owed
        row["net_wealth"] -= row.get("tax_position", Decimal(0))
        deflator = Decimal(str((1 + scenario.inflation) ** ((end - scenario.start).days / 365.25)))
        row["real_net_wealth"] = money(row["net_wealth"] / deflator)
        rows.append(row)
    if compensation:
        rows[-1]["employer_event_log"] = compensation.log
    return rows
