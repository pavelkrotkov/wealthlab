"""Same105000capital, flat marks and actual80000/70000independent source gains."""

from copy import deepcopy

from qoz_cases import flat

from wealthlab.markets.qoz_example import binding, market_case, policy_source
from wealthlab.optimization.inputs import PolicySearch


def offer(identity, plan):
    return dict(
        id=identity,
        provenance="illustration",
        plan=plan,
        source=(
            "Original complete synthetic QOZ decision profile; no sponsor or legal certification"
        ),
        source_date="2026-12-31",
        complete_cash_tax_and_terms_confirmed=True,
        profile_valid_for_all_candidate_income_and_paths_confirmed=True,
        declined_no_prior_interest_or_obligations_confirmed=plan is None,
    )


def case():
    household = policy_source(flat())
    market = market_case(household, "monte_carlo", "early_crash").model_dump(mode="json")
    market.update(paths=1, expected_annual_inflation=0, annual_inflation_volatility=0)
    for asset in market["assets"]:
        asset.update(expected_annual_mark_return=0, annual_volatility=0, annual_cash_yield=0)
    original = household.qoz_plan.model_dump(mode="json")
    half = deepcopy(original)
    half["calls"][0]["amount"] = "40000"
    reference = dict(
        original,
        mode="liquid_reference",
        federal="denied",
        new_jersey="denied",
        settlement_months=0,
    )
    names = ("no_entry", "half", "full", "reference")
    return PolicySearch.model_validate(
        dict(
            household=household,
            binding=binding(),
            training=market,
            validation=dict(market, seed=market["seed"] + 1),
            qoz_offers=[
                offer(n, p) for n, p in zip(names, [None, half, original, reference], strict=True)
            ],
            dimensions=[
                dict(id="qoz_participation", choices=[dict(id=n, qoz_offer=n) for n in names])
            ],
            targets=dict(target_age=50, reserve_years=0, maximum_issuer_weight=None),
        )
    )


def changed(profile, edit):
    data = profile.model_dump(mode="json")
    edit(data)
    return PolicySearch.model_validate(data)
