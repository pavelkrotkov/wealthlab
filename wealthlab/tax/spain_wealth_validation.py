"""Ownership/exemption rules bound each related debt before entering the wealth base."""

from wealthlab.tax.spain_debt_validation import validate_debt
from wealthlab.tax.spain_money import year_end


def validate(case):
    for asset in case.assets:
        validate_asset(case.year, asset)
    home = sum(a.exemption_eur for a in case.assets if a.treatment == "principal_home")
    if home > 300000:
        raise ValueError("Combined principal-home exemptions cannot exceed EUR300000 per person.")
    assets = {a.id: a for a in case.assets}
    for debt in case.debts:
        validate_debt(case.year, debt, assets)


def validate_asset(year, asset):
    year_end(asset.fiscal_value, year)
    owned = asset.fiscal_value.euros() * asset.ownership_share
    if asset.exemption_eur > owned:
        raise ValueError("An exemption cannot exceed the person's fiscal asset value.")
    if asset.treatment in {"included", "unknown"} and asset.exemption_eur:
        raise ValueError("Included/unresolved asset classifications cannot claim an exemption.")
    if asset.treatment == "principal_home" and (asset.kind != "property" or asset.nonproductive):
        raise ValueError("A principal home is property and is not excluded as nonproductive.")
