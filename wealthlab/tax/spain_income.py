"""Compute separate state/regional quotas from independently prelimited recognized bases."""

from decimal import Decimal

from wealthlab.tax.spain_rates import REGIONS, SAVINGS, STATE, scale

ZERO = Decimal(0)


def calculate(case):
    bases = {
        name: max(
            ZERO,
            sum(
                (
                    i.euros()
                    for i in case.incomes
                    if i.spanish_base == name and i.treatment == "allowed"
                ),
                ZERO,
            ),
        )
        for name in ("general", "savings")
    }
    general, savings = reduced(case, bases)
    state = quotas(general, savings, case.state_minimum_eur, STATE)
    regional = quotas(general, savings, case.regional_minimum_eur, REGIONS[case.region])
    gross = state["general"] + regional["general"] + state["savings"] + regional["savings"]
    state_credit = min(sum(state.values()), case.credits.irpf_state)
    regional_credit = min(sum(regional.values()), case.credits.irpf_regional)
    return dict(
        bases=bases,
        liquidable_general=general,
        liquidable_savings=savings,
        state=state,
        regional=regional,
        gross_quota=gross,
        credits=state_credit + regional_credit,
        liability=gross - state_credit - regional_credit,
    )


def reduced(case, bases):
    if (
        case.general_reduction_eur > bases["general"]
        or case.savings_reduction_eur > bases["savings"]
    ):
        raise ValueError("Prelimited reductions cannot exceed their corresponding positive base.")
    return (
        bases["general"] - case.general_reduction_eur,
        bases["savings"] - case.savings_reduction_eur,
    )


def quotas(general, savings, minimum, rows):
    return dict(
        general=max(ZERO, scale(general, rows) - scale(min(general, minimum), rows)),
        savings=max(
            ZERO,
            scale(savings, SAVINGS) - scale(min(savings, max(ZERO, minimum - general)), SAVINGS),
        ),
    )
