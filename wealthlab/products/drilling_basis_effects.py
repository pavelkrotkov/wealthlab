"""Actual applied basis changes remain independent from current tax-loss recognition.

Nondeductible noncapital expenses can reduce outside basis. Each supplied
jurisdiction/at-risk effect needs its own source and remains bounded by the
actual funded pools; denial never independently determines those effects.
"""

from wealthlab.products.drilling_basis import reduce_basis


def apply(ledger, item, available):
    before = dict(ledger.bases)
    tangible = dict(ledger.tangible_basis)
    reduce_basis(ledger.bases, item, available)
    if item.component == "depreciation":
        for key in available:
            ledger.tangible_basis[key] -= min(
                getattr(item, key + "_basis_reduction"), available[key]
            )
    return dict(
        source=item.basis_effect_source,
        requested=dict(
            federal=item.federal_basis_reduction,
            nj=item.nj_basis_reduction,
            at_risk=item.at_risk_reduction,
        ),
        before=before,
        after=dict(ledger.bases),
        applied={key: amount - ledger.bases[key] for key, amount in before.items()},
        tangible_applied={
            key: amount - ledger.tangible_basis[key] for key, amount in tangible.items()
        },
        classification="Supplied basis/at-risk effects; separate from tax recognition",
    )
