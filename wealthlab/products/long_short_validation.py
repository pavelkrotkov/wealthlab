"""Reject inconsistent supplied terms and malformed batches before any capital moves."""

from datetime import timedelta

from wealthlab.products.long_short_paths import periods
from wealthlab.products.long_short_paths import validate as validate_batch


def validate(case, batch, indices):
    validate_terms(case, batch.assets)
    if not indices or len(indices) != len(set(indices)):
        raise ValueError("Select unique long/short path indices.")
    if any(not 0 <= i < len(batch.mark_returns) for i in indices):
        raise ValueError("Long/short path index is outside the realized batch.")
    validate_batch(batch)
    validate_redemptions(case.redemptions, batch)


def validate_redemptions(records, batch):
    ends = {end - timedelta(days=1) for _, end in periods(batch)}
    if len({r.id for r in records}) != len(records):
        raise ValueError("Redemption IDs must be unique.")
    if any(r.date not in ends or r.provenance == "unresolved" for r in records):
        raise ValueError("Resolve month-end redemption assumptions inside the realized horizon.")


def validate_terms(case, assets):
    if not case.terms_confirmed:
        raise ValueError("Confirm the supplied monthly margin, fee and short-proceeds terms.")
    if {case.long_factor, case.short_factor} - set(assets):
        raise ValueError("Unknown long/short market factor.")
    gross = case.long_multiple + case.short_multiple
    if gross == 0 or case.maintenance_fraction_of_gross * gross > 1:
        raise ValueError("Opening exposure must be positive and satisfy supplied maintenance.")
