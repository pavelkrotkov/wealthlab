"""Collectible price paths cannot invent ordinary issuer distributions."""


def validate(scenario, batch, binding):
    if scenario.lot_plan is None:
        return
    securities = {s.id: s for s in scenario.lot_plan.case.securities}
    for item in binding.securities:
        if securities[item.security_id].kind == "collectible":
            factor = batch.assets.index(item.factor)
            if batch.cash_yields[:, :, factor].any():
                raise ValueError(
                    "Collectible market paths require zero cash yield; "
                    "product cash flows need a separate adapter."
                )
