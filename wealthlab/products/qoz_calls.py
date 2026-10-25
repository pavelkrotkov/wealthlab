"""Fund one real capital call and preserve its eligible source-disposal identity.

Eligibility is conditional; tax events only adjust recognition after actual
cash leaves the shared wallet. A gain cannot support duplicate elections.
"""

from wealthlab.products import qoz_economics as economics
from wealthlab.products import qoz_source, qoz_tax
from wealthlab.products.qoz_reconciliation import route_exclusion
from wealthlab.products.qoz_units import new_units


def fund(state, call, wallet):
    row, sold, deadline = qoz_source.source(
        state.lots, call, state.plan.prior_source_year_revision_assumed_confirmed
    )
    funded = min(wallet.cash, call.amount)
    federal = qoz_source.elected_amount(
        row, funded, "federal", state.plan.federal, state.used, call.date <= deadline
    )
    nj_treatment = state.plan.new_jersey if federal else "denied"
    nj = qoz_source.elected_amount(
        row, funded, "new_jersey", nj_treatment, state.used, call.date <= deadline
    )
    elected = dict(federal=federal, new_jersey=nj)
    units = new_units(state, call, funded, elected)
    paid = wallet.pay(call.amount)
    assert paid == funded
    economic_entry = contribute(state, call, funded)
    audit = dict(
        call=call.model_dump(mode="json"),
        source=dict(row),
        funded=funded,
        deadline=deadline.isoformat(),
        elected=elected,
        units=units,
        economic_entry=economic_entry,
        regime="legacy_2026" if call.date.year <= 2026 else "post_2026",
    )
    exclusion = qoz_tax.event(
        call.date,
        "Actual QOZ reinvestment election; no cash tax saving",
        federal=-elected["federal"],
        nj=-elected["new_jersey"],
        character=row["federal_character"],
    )
    exclusion = route_exclusion(state, sold, call, exclusion, audit)
    if not funded:
        return None, exclusion, audit
    tranche = dict(
        id=call.id,
        units=units,
        funded=funded,
        invested=call.date,
        dividends=0,
        tax=qoz_tax.opening(funded, elected, call.date, row["federal_character"]),
    )
    return tranche, exclusion, audit


def contribute(state, call, funded):
    if not funded:
        return {}
    if state.economic is None:
        state.economic = economics.create(state.plan, funded, call.date)
        return dict(
            initial_subscription=funded,
            entry_cost=state.economic["entry_cost"],
            entry_margin=state.economic["entry"],
        )
    return economics.subscribe(state.economic, funded, call.date)
