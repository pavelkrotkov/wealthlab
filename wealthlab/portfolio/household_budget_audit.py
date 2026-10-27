"""Final observed trades can revise a forecast estimate; actual tax/cash remain separate."""

from datetime import date
from decimal import Decimal

from wealthlab.portfolio.household_budget import context
from wealthlab.portfolio.tax_budget import impact
from wealthlab.portfolio.tax_recognition import gains


def audit(lots):
    return [
        entry(lots, decision)
        for decision in lots.sale_decisions
        if decision["mode"] == "tax_budget"
    ]


def observed_on(lots, year):
    # January facts may finalize a prior return after the cash horizon, under
    # its existing explicit no-replacement assumption. Preserve both dates.
    revisions = [
        date.fromisoformat(item["observed"])
        for item in lots.reconciliations
        if item["year"] <= year
    ]
    return max([lots.when, *revisions])


def entry(lots, decision):
    policy = next(item for item in lots.case.sale_policies if item.id == decision["policy"])
    observed = observed_on(lots, policy.date.year)
    view, _forecast = context(lots.plan, policy)
    estimate = impact(view, lots.book, observed, through_year=policy.date.year)
    federal, nj, pending = gains(lots.book, policy.date.year)
    budget = policy.tax_budget
    assert budget is not None
    return dict(
        policy=policy.id,
        decision_date=policy.date.isoformat(),
        forecast_id=decision["forecast_id"],
        forecast_source=decision["forecast_source"],
        forecast_fingerprint=decision["forecast_fingerprint"],
        tax_budget=budget,
        estimated_delta_at_decision=decision.get("estimated_incremental_liability"),
        estimated_budget_met_at_decision=decision.get("budget_met"),
        estimate_after_observed_trades=estimate,
        estimated_budget_met_after_observed_trades=estimate <= budget,
        tax_information_observed_on=observed.isoformat(),
        cash_observed_through=lots.when.isoformat(),
        terminal_wash_assumption_used=observed > lots.when,
        actual_lot_short_term=federal["short_term"],
        actual_lot_long_term=federal["long_term"],
        actual_nj_lot_gain=nj,
        pending_federal_loss=pending["federal"],
        pending_nj_loss=pending["nj"],
        **actual_return(lots.taxes, policy.date.year),
        scope="Forecast liability delta is distinct from actual total liability and net paid cash",
    )


def actual_return(taxes, year):
    closed = taxes.closed_returns.get(year)
    if closed is None:
        if taxes.case.policy.year != year:
            raise ValueError("The budget audit needs an observed actual return for this year.")
        result = taxes.result
        paid = sum(taxes.case.payments.model_dump().values(), Decimal(0))
    else:
        result = closed.result
        paid = sum(closed.net_paid.values(), Decimal(0))
    status = "closed" if closed is not None else "partial"
    if year in taxes.provisional_returns:
        status = "provisional"
    return dict(
        actual_tax_year=year,
        actual_return_status=status,
        actual_total_liability=result["total_liability"],
        actual_net_cash_tax_paid=paid,
    )
