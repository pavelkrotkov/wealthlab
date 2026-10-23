"""Splits preserve share order and replacement usage across independent jurisdiction ledgers."""

from decimal import Decimal as D

from test_nj_wash import nj_case

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


def test_nj_split_of_federally_used_shares_cannot_make_them_available_again():
    """Federal loss on 100 shares but NJ loss on only 40 creates different matches.

    Splitting the 100 federally matched shares for NJ must copy federal usage to
    both pieces, preventing a later federal loss from reusing either piece.
    """
    payload = nj_case(quantity="100")
    original = payload["lots"][0]
    original.update(quantity="40", federal_basis="400", nj_basis="400")
    payload["lots"].append(
        dict(original, id="nj_gain", quantity="60", federal_basis="600", nj_basis="300")
    )
    payload["lots"].append(
        dict(original, id="later", quantity="10", federal_basis="100", nj_basis="100")
    )
    sale = payload["trades"][0]
    sale.update(selection="specific", lot_ids=["original", "nj_gain"])
    payload["trades"].append(
        dict(sale, id="later_sale", date="2026-06-21", quantity="10", lot_ids=["later"])
    )
    result = run(LotCase.model_validate(payload))
    later = result["disposals"][-1]
    assert later["federal_wash_disallowed"] == 0
    assert later["nj_wash_disallowed"] == 25
    assert sum(D(lot["federal_basis"]) for lot in result["lots"]) == 1050
    assert sum(D(lot["nj_basis"]) for lot in result["lots"]) == 925


def test_split_ids_are_never_reused_after_disposal():
    """A used-and-sold split ID must not poison a later unused replacement slice."""
    payload = nj_case(quantity="150")
    payload["accounts"][1]["cash"] = "1500"
    payload["lots"][0].update(quantity="50", federal_basis="500", nj_basis="500")
    payload["lots"].append(dict(payload["lots"][0], id="later"))
    sale = payload["trades"][0]
    sale.update(quantity="50", selection="specific", lot_ids=["original"])
    payload["trades"].extend(
        [
            dict(
                sale,
                id="exit_matched",
                date="2026-06-21",
                account_id="replacement_account",
                price="20",
                lot_ids=["replacement_wash_1"],
            ),
            dict(sale, id="second_loss", date="2026-06-22", lot_ids=["later"]),
        ]
    )
    result = run(LotCase.model_validate(payload))
    assert result["disposals"][-1]["federal_wash_disallowed"] == 125
    assert result["disposals"][-1]["nj_wash_disallowed"] == 125
    assert "replacement_wash_1" not in {lot["id"] for lot in result["lots"]}
    assert "replacement_wash_2" in {lot["id"] for lot in result["lots"]}
