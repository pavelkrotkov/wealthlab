"""Derived tax slices preserve original receipts and independent source/basis splits."""

from dataclasses import dataclass

from wealthlab.tax.pr_decree import pre_rate, rate
from wealthlab.tax.pr_gain_allocation import allocation
from wealthlab.tax.pr_residence import local_period
from wealthlab.tax.pr_source_facts import SourceIncome


@dataclass(frozen=True)
class Slice:
    row: SourceIncome
    treatment: str = "ordinary"


def prepare(comparison, *, incentivized=False):
    assets = {asset.income_index: asset for asset in comparison.gains}
    if len(assets) != len(comparison.gains):
        raise ValueError("Each original receipt can have only one marketable-gain allocation.")
    if any(index >= len(comparison.annual.income) for index in assets):
        raise ValueError("Gain allocation references an absent income row.")
    slices, audits = [], []
    for index, row in enumerate(comparison.annual.income):
        if row.kind == "long_term":
            if index not in assets:
                raise ValueError("Every capital gain needs its dated asset/basis allocation.")
            derived, audit = gain_slices(comparison, assets[index], row, incentivized)
            slices.extend(derived)
            audits.append(audit)
        else:
            treatment = passive_treatment(comparison.decree, row, incentivized)
            slices.append(Slice(row, treatment))
    return slices, audits


def gain_slices(comparison, asset, row, incentivized):
    # Split both recognized bases independently while keeping one receipt date.
    # A federal-US amount need not equal the local pre-residence amount.
    if row.owner != "primary":
        raise ValueError("The gain-allocation profile currently supports the primary owner only.")
    validate_sale_residence(comparison, row)
    audit = allocation(asset, row)
    pre_source = "US" if audit["federal_lookback"] else "PR"
    post_source = "US" if audit["federal_lookback"] and not audit["federal_election"] else "PR"
    # Zero federal/positive PR components remain explicit: after the federal
    # lookback ends, local pre-move appreciation can still have its own tax.
    pre = row.model_copy(
        update={
            "federal_amount": audit["federal_pre_value"],
            "pr_amount": audit["pr_pre"],
            "federal_source": pre_source,
            "pr_source": "US",
        }
    )
    post = row.model_copy(
        update={
            "federal_amount": audit["federal_post_value"],
            "pr_amount": audit["pr_post"],
            "federal_source": post_source,
            "pr_source": "PR",
        }
    )
    before, after = "lt15", "lt15"
    # Denied/unset decree alternatives use the same sources and basis; only
    # the local tax treatment changes in the separately qualified branch.
    if incentivized:
        selected = rate(comparison.decree, row.received)
        if selected is not None:
            before = pre_treatment(comparison.decree, row.received, asset.pr_resident_since)
            after = f"special{selected}"
    return [Slice(pre, before), Slice(post, after)], audit


def passive_treatment(decree, row, incentivized):
    if incentivized and row.kind in {"interest", "dividends"}:
        selected = rate(decree, row.received)
        if selected is not None:
            return f"special{selected}"
    return "ordinary"


def pre_treatment(decree, received, resident_since):
    return "special5" if pre_rate(decree, received, resident_since) == 5 else "lt15"


def validate_sale_residence(comparison, row):
    annual = comparison.annual
    if annual.primary.federal_bfr not in {"full_year", "move_in"}:
        raise ValueError("Stock gains require full-year BFR or qualifying move-in residence.")
    period = local_period(annual.primary, annual.baseline.policy.year)
    if period is None or not period[0] <= row.received <= period[1]:
        raise ValueError("Supported stock sale must occur during explicit local PR residence.")
