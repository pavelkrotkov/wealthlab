"""Finite paired checks include a blocked exit without changing the selected policy."""

from optimization_cases import flat

from wealthlab.markets.household_example import synthetic as markets
from wealthlab.optimization.inputs import PolicySearch


def case():
    data = flat().model_dump(mode="json")
    flat_market = dict(data["training"], mode="deterministic", paths=1)
    crash = dict(
        flat_market,
        mode="stress",
        shocks=[dict(name="early_crash", month=0, mark_shocks=dict(equities=-0.4))],
    )
    lock = dict(
        flat_market,
        mode="stress",
        shocks=[dict(name="exit_lock", month=23, lock_months=dict(equities=1))],
    )
    data["robustness"] = {
        "flat": dict(market=flat_market),
        "invented_history": dict(market=markets("historical")[1].model_dump(mode="json")),
        "crash": dict(market=crash),
        "exit_lock": dict(market=lock),
    }
    return PolicySearch.model_validate(data)
