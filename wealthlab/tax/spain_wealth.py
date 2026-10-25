"""Reconcile IP/ITSGF caps before regional bonuses and actual-paid IP credit.

Model714box40 feeds Model718box152; Model718box205 instead uses actual
IP paid. A calculated IP bill never automatically becomes a credit.
"""

from decimal import Decimal

from wealthlab.tax import spain_regional_policy
from wealthlab.tax.spain_rates import SOLIDARITY, scale
from wealthlab.tax.spain_wealth_limits import limit_facts, limited
from wealthlab.tax.spain_wealth_values import balances

ZERO = Decimal(0)


def paid(case, tax_type):
    return sum(
        (
            p.recognized_tax_eur * (-1 if p.kind == "refund" else 1)
            for p in case.payments
            if p.tax_type == tax_type
        ),
        ZERO,
    )


def calculate(case, income):
    balance = balances(case)
    limits = limit_facts(case, income)
    regional_policy = spain_regional_policy.policy(case.region)
    minimum = (
        case.wealth_allowance.minimum_eur
        if case.wealth_allowance is not None
        else Decimal(regional_policy["wealth_minimum"])
    )
    rows = regional_policy["wealth"]
    ip_base = max(ZERO, balance["net_base"] - minimum)
    sgf_base = max(ZERO, balance["net_base"] - Decimal(700000))
    ip = limited(
        scale(ip_base, rows), balance, limits["adjusted_irpf_quota"], limits["combined_ceiling"]
    )
    sgf = limited(
        scale(sgf_base, SOLIDARITY),
        balance,
        limits["adjusted_irpf_quota"] + ip["capped_quota"],
        limits["combined_ceiling"],
    )
    bonus = spain_regional_policy.bonus(case, ip["capped_quota"], sgf["capped_quota"])
    ip_liability = max(
        ZERO,
        ip["capped_quota"] - case.credits.wealth_foreign - case.credits.wealth_regional - bonus,
    )
    ip_paid = paid(case, "wealth")
    if ip_paid > ip_liability:
        raise ValueError("IP payments above the assessed bill need a separate overpayment adapter.")
    return dict(
        **balance,
        **limits,
        wealth_minimum=minimum,
        supplied_wealth_allowance=(
            case.wealth_allowance.model_dump(mode="json") if case.wealth_allowance else None
        ),
        wealth_taxable_base=ip_base,
        solidarity_taxable_base=sgf_base,
        wealth=ip,
        solidarity=sgf,
        madrid_bonus=bonus if case.region == "madrid" else ZERO,
        regional_bonus=bonus,
        regional_relief_source=case.credits.source,
        regional_policy=regional_policy,
        wealth_liability=ip_liability,
        wealth_actually_paid=ip_paid,
        solidarity_liability=max(
            ZERO, sgf["capped_quota"] - case.credits.solidarity_foreign - ip_paid
        ),
    )
