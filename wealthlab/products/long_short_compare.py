"""An economic comparison requires equal starting capital and the same realized batch."""

from wealthlab.products.long_short_run import run


def compare(sleeve, reference, batch, indices=None):
    if (sleeve.opening_equity, sleeve.outside_cash) != (
        reference.opening_equity,
        reference.outside_cash,
    ):
        raise ValueError(
            "Paired sleeve comparisons require the same investor capital and outside cash."
        )
    if (
        reference.short_multiple
        or reference.long_multiple > 1
        or reference.maintenance_fraction_of_gross != 1
    ):
        raise ValueError(
            "The reference needs no shorts, at most 100% longs and 100% gross maintenance."
        )
    indices = None if indices is None else list(indices)
    left, right = run(sleeve, batch, indices), run(reference, batch, indices)
    differences = [
        dict(
            path=a["path"],
            pre_tax_wealth_difference=a["summary"]["ending_investor_wealth"]
            - b["summary"]["ending_investor_wealth"],
        )
        for a, b in zip(left["details"], right["details"], strict=True)
    ]
    return dict(sleeve=left, reference=right, differences=differences, batch=batch.export())
