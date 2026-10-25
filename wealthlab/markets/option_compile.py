"""Compound only observed monthly price factors; missing option quotes remain missing."""

from datetime import timedelta
from decimal import Decimal

from wealthlab.household.calendar import months
from wealthlab.products.option_inputs import OptionMark


def marks(scenario, batch, binding, index):
    case = scenario.option_plan.case
    spots = dict(stock=case.marks[0].stock, index=case.marks[0].index)
    result = [mark(scenario.start, spots, binding, batch)]
    factors = {name: batch.assets.index(getattr(binding, f"{name}_factor")) for name in spots}
    for month, (_, end) in enumerate(months(scenario.start, scenario.end)):
        for name, factor in factors.items():
            spots[name] *= Decimal(str(1 + batch.mark_returns[index, month, factor]))
            spots[name] = spots[name].quantize(Decimal(".00000001"))
            if spots[name] <= 0:
                raise ValueError("Option spot rounded to zero; terminal write-off is unsupported.")
        result.append(mark(end - timedelta(days=1), spots, binding, batch))
    return result


def mark(day, spots, binding, batch):
    values = {
        key: getattr(binding, key)
        for key in ("rate", "stock_vol", "index_vol", "stock_yield", "index_yield")
    }
    return OptionMark(
        date=day,
        **spots,
        **values,
        source=f"Counterfactual model marks; no option quotes; batch {batch.metadata['batch_id']}",
    )


def compile_plan(payload, scenario, batch, binding, index):
    if binding.options is None:
        return
    compiled = marks(scenario, batch, binding.options, index)
    payload["option_plan"]["case"]["marks"] = [item.model_dump(mode="json") for item in compiled]
    payload["option_plan"]["case"]["holdings"]["closing_prices"] = {
        "STOCK": str(compiled[-1].stock)
    }
