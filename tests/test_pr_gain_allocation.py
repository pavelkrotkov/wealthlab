"""Independent Pub570 FMV example and separate local/federal basis boundaries."""

from datetime import date
from decimal import Decimal

import pytest

from wealthlab.tax.pr_decree_facts import MarketableGain
from wealthlab.tax.pr_gain_allocation import allocation
from wealthlab.tax.pr_source_facts import SourceIncome


def example():
    row = SourceIncome(
        received=date(2025, 12, 31),
        kind="long_term",
        federal_amount=Decimal(6000),
        pr_amount=Decimal(6000),
    )
    asset = MarketableGain(
        income_index=0,
        acquired=date(2010, 1, 1),
        sale_proceeds=Decimal(7000),
        federal_cost=Decimal(1000),
        pr_cost=Decimal(1000),
        federal_possession_start=date(2023, 1, 1),
        pr_resident_since=date(2023, 1, 1),
        federal_move_fmv=Decimal(2000),
        pr_move_fmv=Decimal(2000),
        ordinary_public_stock_classification="assumed",
        actively_traded_throughout="assumed",
        continuous_residence="assumed",
        us_non_bfr_in_prior_ten_years="yes",
        federal_fmv_election="confirmed",
    )
    return asset, row


def test_pub570_marketable_election_uses_actual_first_day_fmv():
    # Published example: cost 1,000, move FMV 2,000, sale 7,000.
    # The election produces US 1,000 / territory 5,000, not blanket exclusion.
    asset, row = example()
    result = allocation(asset, row)
    assert result["federal_us"] == 1000
    assert result["federal_pr"] == 5000
    assert result["pr_pre"] == 1000
    assert result["pr_post"] == 5000


def test_no_election_and_ended_ten_tax_year_lookback_are_different_paths():
    asset, row = example()
    assert (
        allocation(asset.model_copy(update={"federal_fmv_election": "fails"}), row)["federal_us"]
        == 6000
    )
    result = allocation(asset.model_copy(update={"us_non_bfr_in_prior_ten_years": "no"}), row)
    assert result["federal_us"] == 0
    assert result["pr_pre"] == 1000


def test_independent_local_fmv_and_basis_do_not_rewrite_federal_gain():
    asset, row = example()
    changed = asset.model_copy(update={"pr_cost": Decimal(500), "pr_move_fmv": Decimal(2500)})
    result = allocation(changed, row.model_copy(update={"pr_amount": Decimal(6500)}))
    assert result["federal_us"] == 1000
    assert result["pr_pre"] == 2000
    assert result["pr_post"] == 4500


def test_post_move_acquisition_needs_no_preexisting_property_election():
    asset, row = example()
    changed = asset.model_copy(
        update={
            "acquired": date(2023, 3, 1),
            "federal_move_fmv": Decimal(0),
            "pr_move_fmv": Decimal(0),
            "federal_fmv_election": "fails",
        }
    )
    result = allocation(changed, row)
    assert result["federal_pr"] == 6000
    assert result["pr_pre"] == 0


def test_post_move_loss_is_not_clipped_into_a_fictitious_exemption():
    asset, row = example()
    changed = asset.model_copy(update={"sale_proceeds": Decimal(1500)})
    row = row.model_copy(update={"federal_amount": Decimal(500), "pr_amount": Decimal(500)})
    with pytest.raises(ValueError, match="Mixed"):
        allocation(changed, row)


@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("federal_cost", Decimal(999), "reconcile"),
        ("actively_traded_throughout", "unset", "explicit"),
        ("us_non_bfr_in_prior_ten_years", "unset", "history"),
        ("acquired", date(2024, 12, 31), "more than one year"),
    ],
)
def test_unknown_or_inconsistent_asset_facts_guard(field, value, reason):
    asset, row = example()
    with pytest.raises(ValueError, match=reason):
        allocation(asset.model_copy(update={field: value}), row)
