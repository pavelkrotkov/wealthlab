"""Residual gross exposure or unknown tax basis cannot be hidden by a zero marked account."""

from copy import deepcopy

import pytest
from test_qoz_optimizer_exits import closed as closed

from wealthlab.optimization.qoz_exits import completed


@pytest.mark.parametrize(
    "where,key,value",
    [
        ("state", "sold", False),
        ("state", "receivable", ".001"),
        ("state", "settlement", "2028-01-31"),
        ("entity", "long", ".001"),
        ("entity", "cash", ".001"),
        ("entity", "closed", False),
        ("entity", "loan", "NaN"),
        ("entity", "loan", True),
        ("tax", "basis", ".001"),
        ("tax", "ordinary_basis", ".001"),
        ("tax", "included", False),
        ("tax", "elected", None),
        ("entity", "loan", None),
        ("audit", "tranches", []),
        ("audit", "tranches", [None]),
        ("audit", "tranches", [dict(tax=None)]),
    ],
)
def test_remaining_gross_rights_basis_or_malformed_debt_never_certify_exit(
    closed, where, key, value
):
    household, original = closed
    row = deepcopy(original)
    audit = row["qoz_audit"]
    destinations = dict(
        audit=audit,
        state=audit["economic_state"],
        entity=audit["ending_entity"],
        tax=audit["tranches"][0]["tax"]["jurisdictions"]["federal"],
    )
    destinations[where][key] = value
    assert not completed(household, row)


def test_no_qoz_plan_cannot_reuse_a_stale_funded_product_audit(closed):
    household, row = closed
    absent = household.model_copy(update={"qoz_plan": None})
    assert completed(absent, dict(row, qoz_audit=None))
    assert not completed(absent, row)
