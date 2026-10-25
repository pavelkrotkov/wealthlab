"""Fund one real capital call and preserve its eligible source-disposal identity.

Eligibility is conditional; tax events only adjust recognition after actual
cash leaves the shared wallet. A gain cannot support duplicate elections.
"""

from wealthlab.products import qoz_economics as economics
from wealthlab.products import qoz_source, qoz_tax


def fund(state, call, wallet):
    row, _sold, deadline = qoz_source.source(state.lots, call)
    funded = wallet.pay(call.amount)
    federal = qoz_source.elected_amount(
        row, funded, "federal", state.plan.federal, state.used, call.date <= deadline
    )
    nj_treatment = state.plan.new_jersey if federal else "denied"
    nj = qoz_source.elected_amount(
        row, funded, "new_jersey", nj_treatment, state.used, call.date <= deadline
    )
    elected = dict(federal=federal, new_jersey=nj)
    audit = dict(
        call=call.model_dump(mode="json"),
        source=dict(row),
        funded=funded,
        deadline=deadline.isoformat(),
        elected=elected,
        regime="legacy_2026" if call.date.year <= 2026 else "post_2026",
    )
    exclusion = qoz_tax.event(
        call.date,
        "Actual QOZ reinvestment election; no cash tax saving",
        federal=-elected["federal"],
        nj=-elected["new_jersey"],
        character=row["federal_character"],
    )
    if not funded:
        return None, exclusion, audit
    tranche = economics.create(state.plan, funded, call.date)
    tranche.update(
        id=call.id,
        tax=qoz_tax.opening(funded, elected, call.date, row["federal_character"]),
        economic_log=[],
    )
    return tranche, exclusion, audit
