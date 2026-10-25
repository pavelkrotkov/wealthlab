"""Complete original drilling/reference/no-entry offers; no source cash is created.

This starter uses only its original two-year synthetic calendar. Each entire
profile retains supplied costs, tax facts, prices, property quotes and exit
terms. Its checksum is input-edit detection, never sponsor/legal validation.
"""

from wealthlab.markets.example import asset
from wealthlab.optimization.drilling_scope import fingerprint
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.product_example import add_factor
from wealthlab.products.drilling_market_example import synthetic as native


def extend(case):
    example = native("monte_carlo")
    original = example.household
    validate(case, original)
    data = case.model_dump(mode="json")
    data["household"]["accounts"].append(original.accounts[1].model_dump(mode="json"))
    plan = original.drilling_plan.model_dump(mode="json")
    data["household"]["drilling_plan"] = plan
    data["binding"]["drilling"] = example.binding.drilling.model_dump(mode="json")
    data["drilling_offers"] = [
        offer("well", plan),
        offer("shares", dict(plan, mode="liquid_reference")),
        offer("no_entry", None),
    ]
    data["dimensions"].append(
        dict(
            id="drilling_participation",
            choices=[dict(id=o["id"], drilling_offer=o["id"]) for o in data["drilling_offers"]],
        )
    )
    add_prices(data)
    return confirm_synthetic(data)


def offer(identity, plan):
    return dict(
        id=identity,
        provenance="illustration",
        plan=plan,
        source="Original complete synthetic drilling/reference profile; no sponsor or legal terms",
        source_date="2026-01-01",
        complete_matched_terms_confirmed=True,
        mode_change_no_prior_interest_or_obligations_confirmed=identity == "shares",
        declined_no_prior_interest_or_obligations_confirmed=plan is None,
    )


def add_prices(data):
    markets = [
        data["training"],
        data["validation"],
        *(c["market"] for c in data["robustness"].values()),
    ]
    for market in markets:
        add_factor(market, asset("commodity", "other", 0.12, 0.25, 0))
        add_factor(market, asset("reference", "equity", 0.04, 0.15, 0))


def confirm_synthetic(data):
    case = PolicySearch.model_validate(data)
    scope = case.model_dump(mode="json", exclude={"drilling_envelope"})
    envelope = dict(
        id="synthetic_drilling_scope",
        provenance="illustration",
        source=(
            "Original synthetic assumptions for all declared candidates and market paths; "
            "no legal validation"
        ),
        as_of=str(case.household.start),
        valid_through=str(case.household.end),
        search_sha256=fingerprint(scope),
        all_candidate_employment_income_funding_and_bound_price_paths_confirmed=True,
        supplied_legal_se_qbi_amt_history_limits_recapture_release_facts_confirmed=True,
        full_tax_optimization_supported=False,
    )
    return PolicySearch.model_validate(dict(data, drilling_envelope=envelope))


def validate(case, original):
    if not case.household.synthetic:
        raise ValueError("The drilling starter only extends synthetic examples.")
    if case.household.drilling_plan or case.drilling_offers or case.drilling_envelope:
        raise ValueError("The drilling starter cannot replace an existing plan or supplied offers.")
    if (case.household.start, case.household.end) != (original.start, original.end):
        raise ValueError("The original drilling starter requires its complete two-year calendar.")
    if "drilling" in {a.id for a in case.household.accounts}:
        raise ValueError("The drilling starter cannot replace any existing account.")
