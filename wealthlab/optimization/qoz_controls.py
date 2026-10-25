"""Select complete native QOF profiles using original stock, capital and tax assumptions.

The baseline and inactive offers validate before any lock can select them.
One preview path checks factor/calendar scope; execution validates every actual
realized path before moving cash. No-entry clears only the QOF binding while
retaining its zero account and the original source-sale and tax-lot history.
"""

from wealthlab.markets.paths import generate
from wealthlab.markets.qoz_validation import validate as validate_binding
from wealthlab.optimization.qoz_profiles import preserve_account, validate_native, validate_offer


def selected(choices):
    values = [c.qoz_offer for c in choices if c.qoz_offer is not None]
    if len(values) > 1:
        raise ValueError("Only one dimension may select QOZ participation.")
    return values[0] if values else None


def validate(case):
    if case.household.qoz_plan is None:
        if case.qoz_offers:
            raise ValueError("QOZ offers require the original native household plan and account.")
        validate_choices(case)
        return
    validate_native(case.household)
    if len({o.id for o in case.qoz_offers}) != len(case.qoz_offers):
        raise ValueError("QOZ offer identifiers must be unique.")
    for offer in case.qoz_offers:
        validate_offer(case.household, offer)
    validate_choices(case)
    validate_markets(case)


def validate_choices(case):
    known = {o.id for o in case.qoz_offers}
    for dimension in case.dimensions:
        for choice in dimension.choices:
            if choice.qoz_offer is not None and choice.qoz_offer not in known:
                raise ValueError("Every QOZ choice must name a complete supplied offer.")


def validate_markets(case):
    markets = [case.training, case.validation, *(c.market for c in case.robustness.values())]
    plans = [case.household.qoz_plan, *(o.plan for o in case.qoz_offers if o.plan)]
    for market in markets:
        batch = generate(market.model_copy(update={"paths": 1}))
        for plan in plans:
            scenario = case.household.model_copy(update={"qoz_plan": plan})
            validate_binding(scenario, batch, case.binding, 0)


def apply(data, binding, case, choices):
    identity = selected(choices)
    if identity is None:
        return
    offer = next((o for o in case.qoz_offers if o.id == identity), None)
    if offer is None:
        raise ValueError("Select a known QOZ offer.")
    preserve_account(data, case.household)
    data["qoz_plan"] = offer.plan.model_dump(mode="json") if offer.plan else None
    if offer.plan is None:
        binding["qoz"] = None
