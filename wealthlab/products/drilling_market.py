"""Matched actual drilling/reference projections consume one realized price batch."""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.household_run import run
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate
from wealthlab.products.drilling_compare import outcome
from wealthlab.tax.facts import TaxModel


class DrillingMarketCase(TaxModel):
    household: Scenario
    market: MarketCase
    binding: HouseholdBinding


def compare(case):
    scenario = case.household
    if scenario.drilling_plan is None or case.binding.drilling is None:
        raise ValueError("A complete drilling household and explicit price binding are required.")
    batch = generate(case.market)
    policies = {}
    for mode in ("drilling", "liquid_reference"):
        plan = scenario.drilling_plan.model_copy(update={"mode": mode})
        executed = run(scenario.model_copy(update={"drilling_plan": plan}), batch, case.binding)
        policies[mode] = dict(
            batch_id=executed["batch_id"],
            details=executed["details"],
            outcomes=[dict(path=d["path"], **outcome(d["rows"])) for d in executed["details"]],
        )
    return dict(
        inputs=case.model_dump(mode="json"),
        batch=batch.export(),
        policies=policies,
        full_tax_optimization_supported=False,
        scope=(
            "Conditional fixed supplied production/cost/tax/property/exit quotes under "
            "confirmed price envelope; no automatic well valuation or tax eligibility. "
            "Native joint funding includes required product failures; no retirement certificate."
        ),
    )
