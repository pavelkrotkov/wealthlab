"""Run matched benchmark marks through two actual household funding and tax books."""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.products.exchange_fund_direct import validate as validate_direct


def compare(scenario: Scenario):
    if scenario.exchange_fund_plan is None:
        raise ValueError("An exchange-fund plan is required.")
    plan = scenario.exchange_fund_plan
    direct = scenario.model_copy(
        update={"exchange_fund_plan": plan.model_copy(update={"mode": "direct_sale"})}
    )
    exchange = scenario.model_copy(
        update={"exchange_fund_plan": plan.model_copy(update={"mode": "exchange"})}
    )
    validate_direct(direct.exchange_fund_plan)
    rows = {"exchange": project(exchange), "direct_sale": project(direct)}
    return dict(
        rows=rows,
        outcomes={name: outcome(items) for name, items in rows.items()},
        input=scenario.model_dump(mode="json"),
        fund_specific_exclusions_confirmed=plan.fund_specific_flows_excluded_from_direct_sale_confirmed,
    )


def outcome(rows):
    final = rows[-1]
    return dict(
        net_wealth=final["net_wealth"],
        closing_cash=final["closing_cash"],
        locked_value=final["exchange_locked_value"],
        liquid_product_value=final["exchange_liquid_value"],
        funding_failure_months=sum(bool(r["funding_failure"]) for r in rows),
        funding_shortfall=sum(r["funding_shortfall"] for r in rows),
        denied_redemptions=sum(r["exchange_denied_redemptions"] for r in rows),
        tax_position=final.get("tax_position", 0),
        retained_source_quantity=final["exchange_retained_source_quantity"],
        positions_closed=final["exchange_positions_closed"],
        modeled_exit_complete=final["exchange_fund_audit"]["exit_status"]["modeled_exit_complete"],
    )
