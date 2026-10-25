"""Stock-lot units share one entity NAV; rounding cannot create or lose a cent.

The first subscription sets an internal one-unit-per-dollar scale. Later
positive-NAV calls use the pre-call NAV price. Distressed recapitalizations
need supplied issuance terms and cannot infer continuing QOZ tax eligibility.
"""

from decimal import ROUND_DOWN, Decimal

from wealthlab.household.calendar import CENT
from wealthlab.products.long_short_book import ZERO, equity


def new_units(state, call, funded, elected):
    if not funded:
        return ZERO
    if state.economic is None:
        return funded
    nav = equity(state.economic["book"])
    if nav > 0:
        return funded * sum((t["units"] for t in state.tranches), ZERO) / nav
    return recap_units(state, call, funded, elected)


def recap_units(state, call, funded, elected):
    if call.recapitalization_units is None or not call.recapitalization_terms_assumed_confirmed:
        raise ValueError("Nonpositive-NAV recapitalization requires explicit stock issuance terms.")
    prior_elections = [
        j["elected"] for t in state.tranches for j in t["tax"]["jurisdictions"].values()
    ]
    if any([*elected.values(), *prior_elections]):
        raise ValueError(
            "Recapitalization with QOZ elections needs a separately supported tax profile."
        )
    return call.recapitalization_units * funded / call.amount


def allocate(amount, tranches):
    """Largest remainders apportion nonnegative cents, including tiny NAV and unequal lots."""
    if not tranches:
        return []
    total_units = sum((t["units"] for t in tranches), ZERO)
    raw = [amount / CENT * t["units"] / total_units for t in tranches]
    cents = [value.quantize(Decimal(1), rounding=ROUND_DOWN) for value in raw]
    remaining = int(amount / CENT - sum(cents, ZERO))
    order = sorted(range(len(raw)), key=lambda i: raw[i] - cents[i], reverse=True)
    for index in order[:remaining]:
        cents[index] += 1
    return [value * CENT for value in cents]
