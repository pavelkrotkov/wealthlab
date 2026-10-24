"""Federal wash loss is deferred to taxable replacements or denied for IRA replacements."""

from decimal import Decimal as D

import pytest

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run
from wealthlab.portfolio.example import synthetic


def wash_case(wrapper="taxable", quantity="100", end="2026-12-31"):
    payload = synthetic().model_dump(mode="json")
    payload.update(federal_wash_tracking=True, opening_wash_context_complete=True, end=end)
    payload["lots"][0].update(
        federal_basis="1000", nj_basis="1000", economic_basis="1000", quantity="100"
    )
    payload["accounts"].append(
        dict(
            id="replacement_account",
            provenance="assumption",
            owner="spouse",
            wrapper=wrapper,
            cash="1000",
        )
    )
    payload["trades"][0].update(quantity="100", price="7.5", commission="0")
    payload["trades"].append(
        dict(
            payload["trades"][0],
            id="replacement",
            action="buy",
            date="2026-06-20",
            account_id="replacement_account",
            price="8",
            quantity=quantity,
        )
    )
    return LotCase.model_validate(payload)


def test_irs_example_defers_250_into_800_replacement_basis():
    """Pub. 550's $1,000 -> $750 sale followed by an $800 purchase yields $1,050 basis.

    Cash movements remain $750 and $800; the $250 adjustment is never cash income.
    """
    result = run(wash_case())
    loss = result["disposals"][0]
    assert loss["federal_gross_gain"] == -250
    assert loss["federal_wash_disallowed"] == 250
    assert loss["federal_wash_deferred"] == 250
    assert loss["federal_recognized_gain"] == 0
    assert D(result["lots"][0]["federal_basis"]) == 1050
    assert D(result["lots"][0]["nj_basis"]) == 800
    assert result["closing_cash"] == 1950


@pytest.mark.parametrize("wrapper", ["traditional_ira", "roth_ira"])
def test_spouse_ira_replacement_denies_loss_without_basis_increase(wrapper):
    result = run(wash_case(wrapper))
    loss = result["disposals"][0]
    assert loss["federal_wash_permanent"] == 250
    assert loss["federal_wash_deferred"] == 0
    assert D(result["lots"][0]["federal_basis"]) == 800


def test_partial_replacement_preserves_unmatched_loss():
    result = run(wash_case(quantity="40"))
    loss = result["disposals"][0]
    assert loss["federal_wash_disallowed"] == 100
    assert loss["federal_recognized_gain"] == -150
    assert D(result["lots"][0]["federal_basis"]) == 420


def test_unfinished_window_does_not_claim_remaining_loss():
    result = run(wash_case(quantity="40", end="2026-06-25"))
    loss = result["disposals"][0]
    assert loss["federal_recognized_gain"] == 0
    assert loss["federal_pending_loss"] == 150
