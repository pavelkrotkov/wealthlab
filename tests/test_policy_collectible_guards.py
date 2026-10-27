"""Unsupported collectible yield, issuer distributions and stock-style replacements fail closed."""

import pytest
from optimization_collectible_cases import flat

from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.search import search
from wealthlab.portfolio.distribution_inputs import Distribution
from wealthlab.portfolio.distribution_validation import validate_character
from wealthlab.portfolio.harvest_validation import validate_types


def test_realized_collectible_cash_yield_cannot_be_mapped_as_ordinary_dividends():
    case = flat()
    market = case.training.model_copy(update=dict(mode="deterministic"))
    asset = market.assets[0].model_copy(update=dict(annual_cash_yield=0.01))
    batch = generate(market.model_copy(update=dict(assets=[asset])))
    with pytest.raises(ValueError, match="Collectible market paths require zero cash yield"):
        run(case.household, batch, case.binding)


def test_collectible_cannot_use_stock_only_harvest_or_distribution_treatment():
    book = flat().household.lot_plan.case
    security = book.securities[0]
    replacement = security.model_copy(update=dict(id="replacement", kind="etf"))
    with pytest.raises(ValueError, match="collectible replacements"):
        validate_types(book.accounts[0], security, replacement)
    distribution = Distribution(
        id="cash",
        provenance="illustration",
        security_id=security.id,
        ex_date="2026-01-01",
        payment_date="2026-01-31",
        recognition_date="2026-01-31",
        per_share="1",
        federal_character="dividends",
        nj_character="dividends",
    )
    with pytest.raises(ValueError, match="Collectible cash flows"):
        validate_character(distribution, security)


def test_marked_collectible_without_actual_sale_cannot_rank_as_completed_exit():
    data = flat().model_dump(mode="json")
    for choice in data["dimensions"][0]["choices"]:
        choice["sale_policies"] = []
    result = search(PolicySearch.model_validate(data))
    assert result["selection"] is None
    assert all(c["median_real_after_tax_exit_wealth"] is None for c in result["candidates"])
    assert all(not c["constraints"]["completed_after_tax_exit"] for c in result["candidates"])
