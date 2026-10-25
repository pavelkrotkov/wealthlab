"""Synthetic retain-versus-surrender comparison preserves an existing policy's tax history.

Both branches begin with $50,000 cash and $10,000 net policy equity. The supplied
MEC basis is $5,000. Surrender recognizes $5,000 plus conditional $500 additional
tax; retaining the policy later borrows $500 with conditional $50 additional tax.
"""

from copy import deepcopy

from wealthlab.products.life_comparison_example import synthetic as new_policies
from wealthlab.products.life_comparison_inputs import LifeComparison
from wealthlab.products.life_household_example import event
from wealthlab.products.life_household_example import synthetic as existing_policy


def synthetic():
    new = new_policies().model_dump(mode="json")["alternatives"]["liquid_term"]
    keep = existing_policy().model_dump(mode="json")
    keep["name"] = "Retain existing policy with conditional MEC treatment"
    keep["accounts"].append(deepcopy(new["accounts"][1]))
    keep["lot_plan"] = deepcopy(new["lot_plan"])
    keep["lot_plan"]["savings"] = []
    keep["life_plan"]["holdings"][0]["contract"].update(
        opening_federal_basis="5000", federal_status="mec"
    )
    sell = deepcopy(keep)
    sell["name"] = "Supplied surrender plus liquid saving and term"
    old = sell["life_plan"]["holdings"][0]
    old["contract"].update(
        events=[event("opening_exit", "2026-01-01", "surrender", 10000)], values=[]
    )
    old["failure_exits"] = {}
    sell["accounts"].append(deepcopy(new["accounts"][-1]))
    sell["life_plan"]["holdings"].append(deepcopy(new["life_plan"]["holdings"][0]))
    sell["lot_plan"]["savings"] = deepcopy(new["lot_plan"]["savings"])
    return LifeComparison.model_validate(
        dict(
            alternatives=dict(retain=keep, liquid_term=sell),
            liquid_reference="liquid_term",
            term_account_ids=["term"],
            independently_priced_protection_confirmed=True,
        )
    )
