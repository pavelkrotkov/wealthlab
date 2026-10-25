"""Reuse the native PR source/basis/decree slices; indices derive from stable observed IDs.

The same original receipt supplies the native federal/local gain allocations.
Future source rows never enter the current slices. An actual household sale
must also pass the separate native-lot identity/basis check before execution.
"""

from wealthlab.tax.pr_comparison_guards import incentive, profile
from wealthlab.tax.pr_decree_facts import PRComparison
from wealthlab.tax.pr_tax_slices import prepare


def comparison(annual, case):
    context, profile_facts = annual.pr_federal, annual.pr_federal.gain_profile
    gains = linked_gains(context)
    result = PRComparison(
        annual=case,
        decree=profile_facts.decree,
        gains=gains,
        other_preferential_entitlement=profile_facts.other_preferential_entitlement,
        prior_abt_credit=profile_facts.prior_abt_credit,
        description=profile_facts.source,
    )
    reasons = profile(result)
    if reasons:
        raise ValueError("; ".join(reasons))
    return result


def federal(annual, case):
    native = comparison(annual, case)
    slices, audit = prepare(native, incentivized=False)
    return case.model_copy(update=dict(income=[s.row for s in slices])), audit


def local(annual, case):
    native = comparison(annual, case)
    treatment = annual.pr_federal.gain_profile.treatment
    if treatment == "unresolved":
        raise ValueError("Native PR ordinary/decree tax treatment remains unresolved.")
    if treatment == "incentive":
        qualification = incentive(native)
        if not qualification["eligible"]:
            raise ValueError(
                "Native PR decree is unqualified: " + "; ".join(qualification["reasons"])
            )
    slices, audit = prepare(native, incentivized=treatment == "incentive")
    return native, slices, audit


def linked_gains(context):
    validate_links(context)
    observed = [s for s in context.sources if s.income.received <= context.as_of]
    known = {(s.owner_id, s.id): i for i, s in enumerate(observed)}
    return [
        gain.facts.model_copy(update=dict(income_index=known[(gain.owner_id, gain.source_id)]))
        for gain in context.gain_profile.gains
        if (gain.owner_id, gain.source_id) in known
    ]


def validate_links(context):
    all_sources = {(s.owner_id, s.id) for s in context.sources}
    keys = [(g.owner_id, g.source_id) for g in context.gain_profile.gains]
    if len(keys) != len(set(keys)) or any(key not in all_sources for key in keys):
        raise ValueError("Every native PR gain needs one unique known stable person/source link.")
