"""Exact path asset returns replace only returns; native dividends, terms and locks are retained."""

from decimal import Decimal

from wealthlab.products.qoz_inputs import QOZObservation


def observations(scenario, batch, binding, index):
    factor = batch.assets.index(binding.qoz.factor)
    return [
        QOZObservation.model_validate(
            dict(
                original.model_dump(),
                asset_return=Decimal(str(batch.mark_returns[index, month, factor])),
                locked=original.locked or bool(batch.locked[month, factor]),
            )
        )
        for month, original in enumerate(scenario.qoz_plan.observations)
    ]


def compile_plan(payload, scenario, batch, binding, index):
    if binding.qoz is None:
        return
    payload["qoz_plan"]["observations"] = [
        observation.model_dump(mode="json")
        for observation in observations(scenario, batch, binding, index)
    ]
