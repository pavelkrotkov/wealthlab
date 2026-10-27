"""Gross entity assets carry the factor while QOF underlying issuer inventory remains unknown."""

from decimal import Decimal

from tests.qoz_market_cases import flat
from wealthlab.markets.household_run import run


def test_leveraged_entity_exposure_is_not_confused_with_shareholder_nav():
    case, batch, binding = flat()
    economics = case.qoz_plan.economics.model_copy(update=dict(long_multiple=Decimal("1.3")))
    case = case.model_copy(
        update=dict(qoz_plan=case.qoz_plan.model_copy(update=dict(economics=economics)))
    )
    row = run(case, batch, binding)["details"][0]["rows"][0]
    # A funded $80k subscription buys $104k assets with $24k internal creditor debt.
    assert row["qoz_entity_asset_value"] == row["market_factor_values"]["qof_assets"] == 104000
    assert row["qoz_nav"] == 80000
    assert row["qoz_internal_debt"] == 24000
    assert "qoz" not in row["market_unmapped_factor_accounts"]
    assert "qoz" in row["market_unmeasured_issuer_accounts"]
    assert row["market_issuer_concentration_complete"] is False
