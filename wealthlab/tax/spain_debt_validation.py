"""A mortgage does not make the exempt portion of its financed asset deductible."""

from decimal import Decimal

from wealthlab.tax.spain_money import year_end

ZERO = Decimal(0)


def validate_debt(year, debt, assets):
    year_end(debt.balance, year)
    owned = debt.balance.euros() * debt.ownership_share
    if debt.deductible_eur > owned:
        raise ValueError("A debt deduction cannot exceed the person's actual debt share.")
    if debt.related_asset_id is None:
        return
    asset = assets.get(debt.related_asset_id)
    if asset is None:
        raise ValueError("Related debt must identify an entered owned asset.")
    value = asset.fiscal_value.euros() * asset.ownership_share
    deductible = owned * max(ZERO, value - asset.exemption_eur) / value if value else ZERO
    if debt.deductible_eur > deductible:
        raise ValueError("Debt financing an exempt asset portion cannot be deducted again.")
