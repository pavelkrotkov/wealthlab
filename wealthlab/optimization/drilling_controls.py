"""Complete supplied drilling choices retain original capital and an exact input envelope.

The checksum detects edits, not legal eligibility. No tax fact, fee or cash flow
is scaled. Every inactive profile validates before any locked choice executes.
"""

from wealthlab.markets.drilling_compile import validate as validate_binding
from wealthlab.markets.paths import generate
from wealthlab.optimization.drilling_apply import apply as select_offer
from wealthlab.optimization.drilling_profiles import validate_offers


def scope(case):
    return case.model_dump(mode="json", exclude={"drilling_envelope"})


def selected(choices):
    values = [c.drilling_offer for c in choices if c.drilling_offer is not None]
    if len(values) > 1:
        raise ValueError("Only one dimension can select the drilling participation profile.")
    return values[0] if values else None


def validate(case):
    if case.household.drilling_plan is None:
        if case.drilling_offers or case.drilling_envelope is not None:
            raise ValueError("Drilling choices require their original household plan.")
        validate_choices(case)
        return
    if case.drilling_envelope is None:
        raise ValueError("Confirm an independent drilling envelope for this complete search.")
    validate_offers(case.household, case.drilling_offers, case.drilling_envelope, scope(case))
    validate_choices(case)
    validate_markets(case)


def validate_choices(case):
    known = {offer.id for offer in case.drilling_offers}
    for dimension in case.dimensions:
        for choice in dimension.choices:
            if choice.drilling_offer is not None and choice.drilling_offer not in known:
                raise ValueError("Every drilling choice must name a complete supplied offer.")


def validate_markets(case):
    markets = [case.training, case.validation, *(c.market for c in case.robustness.values())]
    plans = [case.household.drilling_plan, *(o.plan for o in case.drilling_offers if o.plan)]
    for market in markets:
        batch = generate(market.model_copy(update={"paths": 1}))
        for plan in plans:
            household = case.household.model_copy(update={"drilling_plan": plan})
            validate_binding(household, batch, case.binding)


def apply(data, binding, case, choices):
    identity = selected(choices)
    if identity is None:
        return
    select_offer(data, case.drilling_offers, identity, case.drilling_envelope, scope(case))
    if data["drilling_plan"] is None:
        binding["drilling"] = None
