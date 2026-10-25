"""Validate supplied value and jurisdiction-specific basket allocation independently."""


def validate_basket(plan):
    ids = [b.security.id for b in plan.basket]
    if len(ids) != len(set(ids)) or plan.source_security.id in ids:
        raise ValueError("Basket securities must be unique and distinct from contributed stock.")
    validate_security_scope(plan)
    validate_weights(plan)
    validate_prices(plan, ids)
    if any(b.federal_holding_start > plan.liquid_after for b in plan.basket):
        raise ValueError("Supplied basket holding starts cannot follow contractual release.")


def validate_prices(plan, ids):
    expected = {plan.source_security.id, *ids}
    for prices in [plan.opening_prices, *(o.prices for o in plan.observations)]:
        if set(prices) != expected:
            raise ValueError("Supply every original-stock and basket price, with no extra marks.")


def validate_weights(plan):
    for field in ("value_weight", "federal_basis_weight", "nj_basis_weight"):
        if sum(getattr(b, field) for b in plan.basket) != 1:
            raise ValueError("Each basket value and independent basis allocation must sum to one.")


def validate_security_scope(plan):
    securities = [plan.source_security, *(b.security for b in plan.basket)]
    if any(s.kind not in {"stock", "etf"} for s in securities):
        raise ValueError("Exchange scope supports ordinary stock/ETF securities only.")
    if len({s.wash_group for s in securities}) != len(securities):
        raise ValueError("Separate basket/source wash groups are required in this bounded profile.")
    generated = {f"exchange_basket_{i}" for i in range(len(plan.basket))}
    if plan.source_lot.id in generated:
        raise ValueError("Source lot ID collides with generated basket lot IDs.")
