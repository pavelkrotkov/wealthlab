"""Marked federal recognition resets at year-end without assuming NJ conformity."""

from decimal import Decimal

import pytest

from tests.option_cases import one_leg, parse
from wealthlab.products.option_engine import run


def test_1256_mark_resets_federal_gain_and_preserves_nj_actual_realization():
    data = one_leg()
    data["legs"][0]["federal_class"] = "section1256"
    result = run(parse(data))
    fed = jurisdiction(result, "federal")
    nj = jurisdiction(result, "nj")
    assert (len(fed), len(nj)) == (2, 1)
    assert total(fed, "recognized") == nj[0]["recognized"] == 1500
    assert total(fed, "long_term") == Decimal(900)
    assert total(fed, "short_term") == Decimal(600)


def test_deferral_cannot_exceed_actual_loss():
    data = one_leg()
    data["tax"]["federal_deferrals"] = {"contract:2026-01-01": "1"}
    with pytest.raises(ValueError, match="exceeds"):
        run(parse(data))


def total(rows, field):
    return sum(row[field] for row in rows)


def jurisdiction(result, name):
    return [row for row in result["tax"] if row["jurisdiction"] == name]
