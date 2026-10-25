"""Required policy failures, dated reserves and protection needs are separate outputs."""

from decimal import Decimal

from wealthlab.products.life_household_calendar import reserve

ZERO = Decimal(0)


def summarize(ledger, rows, values, end):
    coverage = {owner: ZERO for owner in ledger.plan.insurance_need_by_owner}
    for value in values:
        coverage[value["owner"]] += value["net_death_benefit"]
    reserve_target = sum(
        (
            reserve(h, end, ledger.scenario.reserve_years, ledger.books[h.account_id].closed)
            for h in ledger.plan.holdings
        ),
        ZERO,
    )
    return dict(
        life_payment_unfunded=total(rows, "payment_unfunded"),
        life_payments_paid=total(rows, "payment_paid"),
        life_cash_received=total(rows, "received_cash"),
        life_source_tax_withheld=total(rows, "source_tax_withheld"),
        life_premiums_paid=premiums(rows),
        life_retirement_premiums_paid=retired_premiums(ledger, rows),
        life_future_retirement_premiums=future_retired_premiums(ledger, end),
        life_reserve_target=reserve_target,
        life_protection_shortfall=protection_gap(ledger.plan, coverage),
        life_net_death_benefit=sum(coverage.values(), ZERO),
        life_policy_values=values,
    )


def total(rows, key):
    return sum((row[key] for row in rows), ZERO)


def premiums(rows):
    return sum((r["payment_paid"] for r in rows if r["requested_kind"] == "premium"), ZERO)


def protection_gap(plan, coverage):
    return sum(
        (max(ZERO, need - coverage[owner]) for owner, need in plan.insurance_need_by_owner.items()),
        ZERO,
    )


def retired_premiums(ledger, rows):
    retirements = {m.id: m.retirement_date.isoformat() for m in ledger.scenario.members}
    return sum(
        (
            r["payment_paid"]
            for r in rows
            if r["requested_kind"] == "premium"
            and r["date"] >= retirements[ledger.owners[r["account_id"]]]
        ),
        ZERO,
    )


def future_retired_premiums(ledger, end):
    retirements = {m.id: m.retirement_date for m in ledger.scenario.members}
    return sum(
        (
            e.amount
            for h in ledger.plan.holdings
            for e in h.contract.events
            if not ledger.books[h.account_id].closed
            and e.kind == "premium"
            and e.date >= max(end, retirements[ledger.owners[h.account_id]])
        ),
        ZERO,
    )
