"""Coordinate monthly cash, wrapper movements and tax settlement in one wallet.

Employer and IRA movements update their own asset books before household
funding. Their actual cash and recognized tax events enter the shared tax
ledger once; optional requests never create negative account balances.
"""

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
from wealthlab.retirement import ira_household, medicare_household
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
    ira = ira_household.make(scenario)
    medicare = medicare_household.make(scenario)
    for start, end in months(scenario.start, scenario.end):
        medical_events = medicare_household.start(medicare, start)
        events = compensation.month(wallet, start, end) if compensation else ()
        ira_events, ira_summary = ira_household.month(ira, wallet, start, end)
        row = month(
            scenario,
            wallet,
            debt_balances,
            start,
            end,
            fees_owed,
            tax_ledger,
            [*events, *ira_events, *medical_events],
            medicare,
        )
        row.update(ira_summary)
        row.update(medicare_household.observe(medicare, tax_ledger, end))
        if compensation:
            row.update(compensation_snapshot(compensation, wallet, end))
        fees_owed = row["fees_owed"]
        row["net_wealth"] = sum(wallet.balances.values()) - sum(debt_balances.values()) - fees_owed
        row["net_wealth"] -= row.get("tax_position", Decimal(0))
        row["net_wealth"] -= row.get("medicare_owed", Decimal(0))
        deflator = Decimal(str((1 + scenario.inflation) ** ((end - scenario.start).days / 365.25)))
        row["real_net_wealth"] = money(row["net_wealth"] / deflator)
        rows.append(row)
    if compensation:
        rows[-1]["employer_event_log"] = compensation.log
    medicare_household.finish(medicare, rows)
    return rows
