"""One continuous marketable holding period with independently supplied federal/PR bases."""

from decimal import Decimal

from wealthlab.tax.pr_residence import MET


def allocation(asset, row):
    validate(asset, row)
    # Federal FMV is at the first possession tax-home day, which may differ
    # from the local residence date and its independently supplied local FMV.
    federal_pre = asset.federal_move_fmv - asset.federal_cost
    federal_post = asset.sale_proceeds - asset.federal_move_fmv
    pr_pre = asset.pr_move_fmv - asset.pr_cost
    pr_post = asset.sale_proceeds - asset.pr_move_fmv
    if asset.acquired >= asset.federal_possession_start:
        federal_pre, federal_post = Decimal(0), row.federal_amount
    if asset.acquired >= asset.pr_resident_since:
        pr_pre, pr_post = Decimal(0), row.pr_amount
    # Do not discard a post-move loss to manufacture exempt appreciation.
    # Mixed-sign components need their own supported loss-netting computation.
    if min(federal_pre, federal_post, pr_pre, pr_post) < 0:
        raise ValueError("Mixed pre/post losses require a separate netting profile; no clipping.")
    # The federal rule tests preceding tax years. Act60's local five-percent
    # window instead tests elapsed years; one cannot substitute for the other.
    lookback = (
        asset.us_non_bfr_in_prior_ten_years == "yes"
        and asset.acquired < asset.federal_possession_start
    )
    elected = asset.federal_fmv_election in MET
    us_part = federal_pre if lookback else Decimal(0)
    us_part += non_elected_post(federal_post, lookback, elected)
    return dict(
        federal_us=us_part,
        federal_pr=row.federal_amount - us_part,
        federal_pre_value=federal_pre,
        federal_post_value=federal_post,
        pr_pre=pr_pre,
        pr_post=pr_post,
        federal_lookback=lookback,
        federal_election=elected,
        assumptions=asset.model_dump(mode="json"),
    )


def validate(asset, row):
    if row.kind != "long_term":
        raise ValueError("A marketable-gain allocation must reference a long-term income row.")
    if asset.sale_proceeds - asset.federal_cost != row.federal_amount:
        raise ValueError("Sale proceeds/federal cost must reconcile to the original federal gain.")
    if asset.sale_proceeds - asset.pr_cost != row.pr_amount:
        raise ValueError("Sale proceeds/PR cost must reconcile to the original PR gain.")
    validate_dates(asset, row.received)
    validate_claims(asset)


def validate_dates(asset, sold):
    if (asset.acquired.month, asset.acquired.day) == (2, 29):
        raise ValueError("February-29 acquisition holding-period boundary is not supported.")
    if (asset.pr_resident_since.month, asset.pr_resident_since.day) == (2, 29):
        raise ValueError("February-29 local ten-year anniversary needs a separate date profile.")
    anniversary = asset.acquired.replace(year=asset.acquired.year + 1)
    if sold <= anniversary:
        raise ValueError("Supported gain must be held more than one year.")
    if max(asset.federal_possession_start, asset.pr_resident_since) > sold:
        raise ValueError("The supported sale must follow both residence/possession starts.")


def non_elected_post(post, lookback, elected):
    return post if lookback and not elected else Decimal(0)


def validate_claims(asset):
    if asset.ordinary_public_stock_classification not in MET:
        raise ValueError("Ordinary public-stock source/character classification must be explicit.")
    if asset.actively_traded_throughout not in MET or asset.continuous_residence not in MET:
        raise ValueError("Active trading and one continuous residence period need explicit claims.")
    if asset.us_non_bfr_in_prior_ten_years == "unset" or asset.federal_fmv_election == "unset":
        raise ValueError("Federal ten-year history and FMV election must be explicit.")
