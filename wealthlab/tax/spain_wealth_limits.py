"""The published forms distinguish gross, cap-eligible and capped quotas."""

from decimal import Decimal

from wealthlab.household.calendar import money

ZERO = Decimal(0)


def limit_facts(case, income):
    savings = income["bases"]["savings"]
    excluded = case.long_held_gain_cap_exclusion_eur
    if excluded > savings:
        raise ValueError("The prelimited long-held gain exclusion cannot exceed the savings base.")
    savings_quota = income["state"]["savings"] + income["regional"]["savings"]
    excluded_quota = money(savings_quota * excluded / savings) if savings else ZERO
    base = sum(income["bases"].values()) + case.patrimonial_company_dividends_eur - excluded
    return dict(
        adjusted_irpf_quota=income["gross_quota"] - excluded_quota,
        excluded_savings_quota=excluded_quota,
        combined_ceiling=money(base * Decimal(".6")),
    )


def limited(gross, balance, other_quota, ceiling):
    nonproductive_quota = (
        money(gross * balance["nonproductive_net"] / balance["net_base"])
        if balance["net_base"]
        else ZERO
    )
    eligible = gross - nonproductive_quota
    reduction = min(max(ZERO, other_quota + eligible - ceiling), money(gross * Decimal(".8")))
    return dict(
        gross_quota=gross,
        nonproductive_quota=nonproductive_quota,
        cap_eligible_quota=eligible,
        cap_reduction=reduction,
        capped_quota=gross - reduction,
    )
