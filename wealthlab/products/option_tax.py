"""Conditional tax events are separate from cash; no inferred deductible loss or tax saving."""

from wealthlab.household.calendar import money
from wealthlab.products.option_math import direction, units
from wealthlab.products.option_valuation import value


def yearend(state, mark):
    if (mark.date.month, mark.date.day) != (12, 31):
        return
    for leg in state.active.values():
        if leg.federal_class == "section1256":
            cumulative = (
                money(direction(leg) * units(leg) * (value(leg, mark) - leg.premium))
                - leg.opening_fee
            )
            state.recognition.append(
                dict(
                    id=f"{leg.id}:{mark.date}:yearend",
                    leg_id=leg.id,
                    date=mark.date.isoformat(),
                    action="yearend_mark",
                    physical=False,
                    pnl=cumulative,
                    federal_class=leg.federal_class,
                    federal_character=leg.federal_character,
                )
            )


def unresolved(tax, jurisdiction):
    fields = ["straddle", "constructive_sale", "holding_period"]
    if jurisdiction == "federal":
        fields += ["federal_rules", "covered_call"]
    else:
        fields += ["nj_rules", "nj_premium_basis"]
    return [field for field in fields if getattr(tax, field) == "unresolved"]
