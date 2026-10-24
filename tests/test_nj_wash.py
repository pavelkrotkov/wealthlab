"""NJ scenario assumptions use independent loss amounts and preserve federal results."""

from decimal import Decimal as D

import pytest
from test_wash_sales import wash_case

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


def nj_case(mode="federal_rules", **kwargs):
    payload = wash_case(**kwargs).model_dump(mode="json")
    payload["nj_wash_treatment"] = mode
    return payload


def test_same_basis_wash_matches_same_shares_in_both_jurisdictions():
    """Splitting must assign both adjustments to the same first 100 purchased shares.

    Merely matching aggregate basis would miss different future sale consequences.
    """
    payload = nj_case(quantity="150")
    payload["accounts"][1]["cash"] = "1500"
    result = run(LotCase.model_validate(payload))
    assert sorted(
        (D(lot["quantity"]), D(lot["federal_basis"]), D(lot["nj_basis"])) for lot in result["lots"]
    ) == [(D(50), D(400), D(400)), (D(100), D(1050), D(1050))]
    row = result["disposals"][0]
    assert row["nj_wash_deferred"] == 250
    assert row["nj_recognized_gain"] == 0


@pytest.mark.parametrize(
    "federal_basis,nj_basis,expected",
    [
        ("1000", "1200", (250, 450)),
        ("500", "1000", (0, 250)),
        ("1000", "500", (250, 0)),
    ],
)
def test_loss_can_differ_or_exist_in_only_one_jurisdiction(federal_basis, nj_basis, expected):
    # One jurisdiction can have a loss while the other has a gain. Neither may
    # inherit the other ledger's dollar adjustment or its replacement eligibility.
    payload = nj_case()
    payload["lots"][0].update(federal_basis=federal_basis, nj_basis=nj_basis)
    result = run(LotCase.model_validate(payload))
    row = result["disposals"][0]
    assert (row["federal_wash_deferred"], row["nj_wash_deferred"]) == expected
    assert D(result["lots"][0]["federal_basis"]) == 800 + expected[0]
    assert D(result["lots"][0]["nj_basis"]) == 800 + expected[1]
    assert D(result["lots"][0]["economic_basis"]) == 800


def test_nj_unconfirmed_does_not_claim_recognition():
    result = run(LotCase.model_validate(nj_case("unconfirmed")))
    assert result["disposals"][0]["nj_recognized_gain"] is None


def test_explicit_no_wash_counterfactual_does_not_adjust_nj_basis():
    result = run(LotCase.model_validate(nj_case("no_wash_assumption")))
    assert result["disposals"][0]["nj_recognized_gain"] == -250
    assert D(result["lots"][0]["nj_basis"]) == 800


def test_ira_denies_jurisdiction_own_loss_without_raising_basis():
    payload = nj_case(wrapper="roth_ira")
    payload["lots"][0]["nj_basis"] = "1200"
    result = run(LotCase.model_validate(payload))
    assert result["disposals"][0]["nj_wash_permanent"] == 450
    assert D(result["lots"][0]["nj_basis"]) == 800
