"""Native linked disposals must own the proceeds, dates, holding period and federal basis.

This bounded bridge supports specifically identified complete sales of one
opening plain-stock lot. PR basis/FMV remain independently supplied native
facts; neither is silently copied from the federal or NJ lot basis.
"""

from decimal import Decimal

from wealthlab.household.calendar import money, months
from wealthlab.household.flows import amount
from wealthlab.tax.jurisdiction_execution_pr import complete_annual
from wealthlab.tax.pr_execution_context import prepare
from wealthlab.tax.pr_execution_gains import local


def validate(annual, scenario):
    profile = annual.pr_federal.gain_profile
    if profile is None:
        return
    if not profile.source.strip():
        raise ValueError("PR gain profile needs its independent source evidence.")
    if scenario.lot_plan is None:
        raise ValueError("PR household gains require the actual linked household lot book.")
    full = complete_annual(annual)
    local(full, prepare(full)[0])
    validate_costs(profile, scenario, annual.policy.year)
    ids = [gain.sale_trade_id for gain in profile.gains]
    if len(ids) != len(set(ids)):
        raise ValueError("Each PR gain must retain one distinct actual native sale.")
    for gain in profile.gains:
        validate_gain(annual, scenario, gain)


def validate_gain(annual, scenario, gain):
    sources = {(s.owner_id, s.id): s.income for s in annual.pr_federal.sources}
    row = sources[(gain.owner_id, gain.source_id)]
    case = scenario.lot_plan.case
    trades = {t.id: t for t in case.trades}
    trade = trades.get(gain.sale_trade_id)
    if trade is None or trade.action != "sell" or trade.date != row.received:
        raise ValueError("PR gain source must match the actual dated native stock sale.")
    lot = selected_lot(case, trade)
    validate_basis(annual, case, gain, trade, lot)


def validate_basis(annual, case, gain, trade, lot):
    accounts = {a.id: a for a in case.accounts}
    securities = {s.id: s for s in case.securities}
    owner = annual.pr_federal.people[gain.owner_id]
    if (accounts[trade.account_id].owner, securities[trade.security_id].kind) != (owner, "stock"):
        raise ValueError("PR gain must preserve the actual person and plain-stock holding.")
    expected = (
        lot.acquired,
        lot.acquired,
        lot.federal_basis,
        money(trade.quantity * trade.price) - trade.commission,
    )
    actual = (
        gain.facts.acquired,
        lot.federal_holding_start,
        gain.facts.federal_cost,
        gain.facts.sale_proceeds,
    )
    if actual != expected:
        raise ValueError(
            "PR acquisition/holding/basis/net proceeds must match the actual native sale."
        )


def validate_costs(profile, scenario, year):
    if profile.treatment != "incentive":
        return
    cost = profile.decree.annual_compliance_cost
    if cost is None:
        raise ValueError("PR incentives need supplied compliance costs, including explicit zero.")
    if cost == 0:
        return
    expenses = {e.id: e for e in scenario.expenses}
    expense = expenses.get(profile.compliance_expense_id)
    if expense is None:
        raise ValueError("PR compliance costs need an actual dated household expense.")
    paid = expense_total(expense, scenario, year)
    if paid != cost:
        raise ValueError("PR supplied compliance cost and actual dated expense must reconcile.")


def selected_lot(case, trade):
    if trade.selection != "specific" or len(trade.lot_ids) != 1:
        raise ValueError("PR gain execution requires one specifically identified opening lot.")
    lots = {lot.id: lot for lot in case.lots}
    lot = lots.get(trade.lot_ids[0])
    if lot is None or trade.quantity != lot.quantity:
        raise ValueError("PR gain execution requires a complete sale of the opening lot.")
    return lot


def expense_total(expense, scenario, year):
    return sum(
        (
            amount(expense, start, end, scenario)
            for start, end in months(scenario.start, scenario.end)
            if start.year == year
        ),
        Decimal(0),
    )
