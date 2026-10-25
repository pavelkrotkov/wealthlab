"""Complete original profiles use an actual short native household and normalized search inputs."""

from copy import deepcopy

from drilling_cases import short

from wealthlab.markets.inputs import MarketCase
from wealthlab.optimization.drilling_inputs import DrillingEnvelope, DrillingOffer
from wealthlab.optimization.drilling_scope import fingerprint
from wealthlab.optimization.inputs import Dimension, PolicyChoice, PolicySearch
from wealthlab.products.drilling_market_example import synthetic as market_example


def offer(identity, plan, declined=False, mode_change=False):
    return DrillingOffer(
        id=identity,
        provenance="illustration",
        plan=plan,
        source="Original independently supplied complete synthetic profile; no inferred scaling",
        source_date="2026-01-01",
        complete_matched_terms_confirmed=True,
        mode_change_no_prior_interest_or_obligations_confirmed=mode_change,
        declined_no_prior_interest_or_obligations_confirmed=declined,
    )


def inputs():
    household = short()
    plan = household.drilling_plan
    offers = [
        offer("well", plan),
        offer("shares", plan.model_copy(update={"mode": "liquid_reference"}), mode_change=True),
        offer("decline", None, True),
    ]
    return household, offers, *envelope(household, offers)


def envelope(household, offers):
    starter = market_example("monte_carlo")
    data = starter.market.model_dump(mode="json")
    data.update(end=str(household.end), paths=2)
    training = MarketCase.model_validate(data)
    validation = training.model_copy(update={"seed": training.seed + 1})
    case = PolicySearch(
        household=household,
        binding=starter.binding,
        training=training,
        validation=validation,
        dimensions=[Dimension(id="retain", choices=[PolicyChoice(id="unchanged")])],
    )
    scope = case.model_dump(mode="json", exclude={"drilling_envelope"})
    scope["drilling_offers"] = [o.model_dump(mode="json") for o in offers]
    record = DrillingEnvelope(
        id="independent_scope",
        provenance="assumption",
        source="Synthetic independent facts for all declared candidates and price paths",
        as_of=household.start,
        valid_through=household.end,
        search_sha256=fingerprint(scope),
        all_candidate_employment_income_funding_and_bound_price_paths_confirmed=True,
        supplied_legal_se_qbi_amt_history_limits_recapture_release_facts_confirmed=True,
    )
    return record, scope


def opaque_profile(household):
    data = household.drilling_plan.model_dump(mode="json")
    row = data["observations"][0]
    row.update(
        capital_call="40000",
        idc_cost="20000",
        tangible_cost="10000",
        residual_property_value="15000",
        exit_gross_proceeds="25000",
    )
    for item in row["deductions"]:
        if item["component"] == "idc":
            item.update(
                federal_requested="20000",
                nj_requested="20000",
                federal_basis_reduction="20000",
                nj_basis_reduction="20000",
                at_risk_reduction="20000",
            )
    data.update(federal_recapture_limit="20000", nj_recapture_limit="20000")
    return household.drilling_plan.model_validate(deepcopy(data))
