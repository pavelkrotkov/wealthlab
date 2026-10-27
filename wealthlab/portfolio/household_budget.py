"""Only explicit dated annual assumptions enter a temporary native policy forecast view."""

from hashlib import sha256

from wealthlab.portfolio.household_budget_validation import select


def context(plan, policy):
    if policy.mode != "tax_budget":
        return plan.case, None
    forecast = select(plan, policy.date)
    return plan.case.model_copy(update={"lot_tax_cases": forecast.cases}), forecast


def decorate(decision, forecast):
    if forecast is None:
        return decision
    return dict(
        decision,
        forecast_id=forecast.id,
        forecast_source=forecast.source_reference,
        forecast_source_date=forecast.source_date.isoformat(),
        forecast_available_on=forecast.available_on.isoformat(),
        forecast_fingerprint=sha256(forecast.model_dump_json().encode()).hexdigest(),
        budget_met_is_estimate=True,
        budget_scope="Cumulative observed linked-lot events under dated fixed annual forecasts",
    )
