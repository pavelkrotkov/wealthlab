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
from wealthlab.portfolio import household_book, household_wash
from wealthlab.products import household as sleeves
from wealthlab.retirement import (
    education_household,
    hsa_household,
    ira_household,
    medicare_household,
    workplace,
    workplace_rollovers,
)
from wealthlab.retirement.social_household import prepare
from wealthlab.tax.projection_ledger import TaxLedger


def project(scenario: Scenario, market=None) -> list[dict]:
    scenario = prepare(prepare_compensation(prepare_employment(scenario)))
    validate_resolved(scenario)
    wallet = Wallet(scenario)
    debt_balances = debts.opening_debts(scenario)
    rows, fees_owed = [], Decimal(0)
    lots = household_book.make(scenario)
    tax_ledger = TaxLedger(scenario.tax_plan, scenario, lots) if scenario.tax_plan else None
    compensation = CompensationLedger(scenario) if scenario.compensation_plan else None
    ira = ira_household.make(scenario)
    medicare = medicare_household.make(scenario)
    employee = workplace.make(scenario)
    hsa = hsa_household.make(scenario)
    education = education_household.make(scenario)
    products = sleeves.make(scenario)
    household_wash.bind(lots, tax_ledger, ira, medicare, education)
    for start, end in months(scenario.start, scenario.end):
        live, market_events = market.start(scenario, lots, start) if market else (scenario, ())
        medical_events = medicare_household.start(medicare, start)
        events = compensation.month(wallet, start, end) if compensation else ()
        workplace_rollovers.before_ira(employee, wallet, ira, start, end)
        ira_events, ira_summary = ira_household.month(ira, wallet, start, end)
        row = month(
            live,
            wallet,
            debt_balances,
            start,
            end,
            fees_owed,
            tax_ledger,
            [*events, *ira_events, *medical_events, *market_events],
            medicare,
            employee,
            ira,
            hsa,
            education,
            lots,
            products,
        )
        row.update(ira_summary)
        row.update(medicare_household.observe(medicare, tax_ledger, end))
        if compensation:
            row.update(compensation_snapshot(compensation, wallet, end))
        fees_owed = row["fees_owed"]
        row["net_wealth"] = sum(wallet.balances.values()) - sum(debt_balances.values()) - fees_owed
        row["net_wealth"] -= row.get("tax_position", Decimal(0))
        row["net_wealth"] -= row.get("medicare_owed", Decimal(0))
        row["net_wealth"] -= row.get("medical_owed", Decimal(0))
        row["net_wealth"] -= row.get("hsa_investment_fees_owed", Decimal(0))
        row["net_wealth"] -= row.get("sleeve_liability", Decimal(0))
        deflator = Decimal(str((1 + scenario.inflation) ** ((end - scenario.start).days / 365.25)))
        row["real_net_wealth"] = money(row["net_wealth"] / deflator)
        observe_market(market, lots, row)
        rows.append(row)
    finish(rows, compensation, employee, lots, medicare, hsa, education, market, products)
    return rows


def finish(rows, compensation, employee, lots, medicare, hsa, education, market, products):
    if compensation:
        rows[-1]["employer_event_log"] = compensation.log
    if employee:
        rows[-1]["workplace_audit"] = employee.log
        rows[-1]["workplace_market_audit"] = employee.market_log
        rows[-1]["workplace_withdrawal_audit"] = employee.withdrawal_log
        rows[-1]["workplace_rollover_audit"] = employee.rollover_log
        rows[-1]["workplace_rmd_audit"] = employee.rmd.audit if employee.rmd is not None else []
    household_book.finish(lots, rows)
    medicare_household.finish(medicare, rows)
    hsa_household.finish(hsa, rows)
    education_household.finish(education, rows)
    sleeves.finish(products, rows)
    if market:
        market.finish(rows)


def observe_market(market, lots, row):
    if market:
        market.observe(lots, row)
