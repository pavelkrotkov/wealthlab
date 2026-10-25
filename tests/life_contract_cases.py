"""Independent synthetic histories, in dollars, for policy accounting oracles."""

from wealthlab.products.life_contract_example import synthetic
from wealthlab.products.life_contract_inputs import LifeContractCase


def event(kind, amount, day=1, **extra):
    return dict(
        id=f"{kind}_{day}",
        provenance="assumption",
        date=f"2025-06-{day:02}",
        kind=kind,
        amount=str(amount),
        nj_ordinary_income="0",
        **extra,
    )


def case(events=(), **updates):
    data = synthetic().model_dump(mode="json")
    data["annual_cases"] = {}
    data["contract"].update(
        opening_federal_basis="100",
        opening_loan="0",
        values=[],
        events=list(events),
    )
    data["contract"].update(updates)
    return LifeContractCase.model_validate(data)
