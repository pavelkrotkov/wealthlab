"""Net taxable wealth and nonproductive wealth retain related/general debt allocation."""

from decimal import Decimal

from wealthlab.household.calendar import money

ZERO = Decimal(0)


def balances(case):
    assets = {
        a.id: money(a.fiscal_value.euros() * a.ownership_share) - a.exemption_eur
        for a in case.assets
    }
    gross = sum(assets.values(), ZERO)
    debt = sum((d.deductible_eur for d in case.debts), ZERO)
    net = max(ZERO, gross - debt)
    return dict(
        gross_nonexempt=gross,
        deductible_debt=debt,
        net_base=net,
        nonproductive_net=min(net, nonproductive_value(case, assets, gross)),
    )


def nonproductive_value(case, assets, gross):
    ids = {a.id for a in case.assets if a.nonproductive}
    value = sum((v for key, v in assets.items() if key in ids), ZERO)
    linked, unlinked = allocated_debt(case, ids)
    general_share = money(unlinked * value / gross) if gross else ZERO
    return max(ZERO, value - linked - general_share)


def allocated_debt(case, ids):
    return (
        sum((d.deductible_eur for d in case.debts if d.related_asset_id in ids), ZERO),
        sum((d.deductible_eur for d in case.debts if d.related_asset_id is None), ZERO),
    )
