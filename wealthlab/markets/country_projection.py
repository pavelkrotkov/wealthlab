"""Native country reconciliation receives fresh market state on every cash pass.

The country engine reuses the same realized batch and source facts. Month,
liquidity locks, guardrails and CPI cannot leak from an earlier reciprocal pass.
"""

from wealthlab.household.projection import project
from wealthlab.markets.household_execution import Execution
from wealthlab.tax.country_wages import prepare
from wealthlab.tax.jurisdiction_execution import evaluate
from wealthlab.tax.jurisdiction_execution_facts import JurisdictionExecutionCase
from wealthlab.tax.spain_cash_sources import rebind as fiscal_cash


def path(scenario, batch, binding, index, context):
    def market(active):
        return Execution(active, batch, binding, index)

    if context is None:
        if scenario.foreign_tax_plan and any(c.pr_federal for c in scenario.tax_plan.cases):
            raise ValueError("Native country market paths require their fixed country context.")
        return project(scenario, market=market(scenario)), {}
    active, spain = prepare(scenario, context)
    result = evaluate(active, spain=spain, market_factory=market, cash_sources=context.cash_sources)
    resolved = fiscal_cash(active, spain, context.cash_sources, result["rows"])
    country = JurisdictionExecutionCase.model_validate(
        dict(scenario=result["scenario"], spain=resolved)
    )
    return result["rows"], dict(
        country_inputs=country.model_dump(mode="json"),
        country_assessments=result["country_assessments"],
        country_reconciliation=result["reconciliation"],
    )
