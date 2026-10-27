"""Replace only commodity/reference prices and add reference locks on a realized path.

Production, costs, property/exit quotes and prelimited tax facts stay supplied.
Their validity over the realized-price envelope is an independent confirmation,
not a valuation, depletion, QBI, AMT or SE recomputation.
"""

from decimal import Decimal, InvalidOperation

from wealthlab.products.drilling_validation import validate_dates


def validate(scenario, batch, binding):
    selected = binding.drilling
    if scenario.drilling_plan is None:
        if selected is not None:
            raise ValueError("A drilling price binding requires an actual drilling plan.")
        return
    validate_binding(selected, scenario.drilling_plan.account_id, batch.assets)
    validate_returns(batch, selected)
    validate_dates(scenario, scenario.drilling_plan)


def validate_binding(selected, account_id, assets):
    if selected is None or selected.account_id != account_id:
        raise ValueError("Bind the complete actual drilling account to explicit price factors.")
    if not (
        selected.replace_price_observations_confirmed
        and selected.fixed_production_cost_tax_and_property_exit_quotes_valid_for_prices_confirmed
    ):
        raise ValueError(
            "Confirm replacement prices and supplied production/cost/tax/property/exit "
            "quote validity over the realized-price envelope."
        )
    factors = {selected.commodity_factor, selected.reference_factor}
    if len(factors) != 2 or not factors <= set(assets):
        raise ValueError("Drilling requires two distinct known commodity/reference price factors.")


def validate_returns(batch, selected):
    indices = [
        batch.assets.index(f) for f in (selected.commodity_factor, selected.reference_factor)
    ]
    if batch.metadata["return_convention"] != "price_plus_cash":
        raise ValueError("Drilling price proxies require the separate price-plus-cash convention.")
    if (batch.cash_yields[:, :, indices] != 0).any():
        raise ValueError("Drilling price-only proxies cannot consume factor cash yields.")
    if batch.locked[:, indices[0]].any():
        raise ValueError("Locked commodity-sales observations require a separate cash adapter.")
    if (batch.mark_returns[:, :, indices] < -1).any():
        raise ValueError("Drilling price-factor losses cannot exceed one hundred percent.")


def compile_plans(payload, scenario, batch, binding, index):
    if binding.drilling is not None:
        payload["drilling_plan"]["observations"] = observations(scenario, batch, binding, index)


def observations(scenario, batch, binding, index):
    selected = binding.drilling
    plan = scenario.drilling_plan
    commodity = prices(selected.opening_commodity_price, batch, index, selected.commodity_factor, 2)
    reference = prices(plan.opening_reference_price, batch, index, selected.reference_factor, 8)
    if any(price <= 0 for price in reference):
        raise ValueError("Nonpositive reference prices require a separate share write-off adapter.")
    factor = batch.assets.index(selected.reference_factor)
    return [
        dict(
            row.model_dump(mode="json"),
            commodity_price=str(commodity[month]),
            reference_price=str(reference[month]),
            reference_locked=bool(row.reference_locked or batch.locked[month, factor]),
        )
        for month, row in enumerate(plan.observations)
    ]


def prices(opening, batch, index, factor, precision):
    price, result = Decimal(opening), []
    quantum = Decimal(1).scaleb(-precision)
    for change in batch.mark_returns[index, :, batch.assets.index(factor)]:
        try:
            price = (price * (Decimal(1) + Decimal(str(change)))).quantize(quantum)
        except InvalidOperation as error:
            raise ValueError(
                "Drilling price path exceeds the supported Decimal quote range."
            ) from error
        result.append(price)
    return result
