"""Unsupported basis-changing distributions cannot masquerade as ordinary income."""


def validate_distributions(case):
    if case.distributions and not case.price_only_marks_confirmed:
        raise ValueError(
            "Confirm price-only marks; total-return marks would double-count distributions."
        )
    securities = {item.id: item for item in case.securities}
    ids = {
        item.id
        for item in [*case.trades, *case.sale_policies, *case.harvest_policies, *case.fee_schedules]
    }
    for item in case.distributions:
        if item.id in ids or item.provenance == "unresolved":
            raise ValueError("Distribution IDs must be distinct and assumptions resolved.")
        ids.add(item.id)
        validate_event(case, item, securities)


def validate_character(item, security):
    if item.qualified_fraction and security.kind not in {"stock", "etf"}:
        raise ValueError("Qualified-dividend holding rules require common stock or fund shares.")
    if security.kind == "collectible":
        raise ValueError("Collectible cash flows require a separate product model.")


def validate_event(case, item, securities):
    if item.security_id not in securities:
        raise ValueError("Distributions require a configured security.")
    if not case.as_of <= item.ex_date <= case.end:
        raise ValueError("Distribution entitlement must lie inside the case.")
    validate_character(item, securities[item.security_id])
