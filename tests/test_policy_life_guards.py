"""Inactive life alternatives cannot rewrite capital, eligibility or known contract history.

A finite menu is only a decision boundary when every offered path remains a
complete interpretation of the same opening policy and household insurance need.
These cases fail before the stochastic batch runs, including locked alternatives.
"""

import pytest
from optimization_life_cases import case

from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.life_paths import apply, selections
from wealthlab.optimization.validation import validate


@pytest.mark.parametrize(
    "field,value",
    [
        ("opening_federal_basis", "1"),
        ("opening_loan", "1"),
        ("federal_status", "mec"),
        ("additional_tax_exception", "disability_confirmed"),
        ("issue_date", "2021-01-01"),
    ],
)
def test_inactive_paths_cannot_rewrite_basis_debt_or_tax_eligibility(field, value):
    data = case().model_dump(mode="json")
    data["dimensions"][1]["locked_choice"] = "paid_up"
    data["life_opportunities"][2]["holding"]["contract"][field] = value
    with pytest.raises(ValueError, match="preserve opening basis"):
        validate(PolicySearch.model_validate(data))


@pytest.mark.parametrize(
    "mutation,match",
    [
        ("value", "preserve opening values"),
        ("funding", "funding permissions"),
        ("missing_value", "every in-force month"),
        ("missing_failure", "supplied failure exit"),
        ("unconfirmed", "matched life-path"),
        ("unresolved", "matched life-path"),
        ("duplicate", "identifiers must be unique"),
        ("unknown", "supplied path"),
        ("wrong_account", "supplied path"),
        ("wrong_holding", "existing configured policy"),
        ("no_plan", "exactly one policy holding"),
    ],
)
def test_every_offered_path_is_complete_and_explicit_even_when_unselected(mutation, match):
    data = case().model_dump(mode="json")
    offered = data["life_opportunities"][2]
    change(data, offered, mutation)
    with pytest.raises(ValueError, match=match):
        validate(PolicySearch.model_validate(data))


def change(data, offered, mutation):
    holding = offered["holding"]
    actions = {
        "value": lambda: holding["opening_values"].update(gross_cash_value="1"),
        "funding": lambda: holding.update(funding="permitted_household_sales"),
        "missing_value": lambda: holding["contract"]["values"].pop(),
        "missing_failure": lambda: holding["failure_exits"].clear(),
        "unconfirmed": lambda: offered.update(matched_path_terms_assumed_confirmed=False),
        "unresolved": lambda: offered.update(provenance="unresolved"),
        "duplicate": lambda: data["life_opportunities"].append(offered),
        "unknown": lambda: data["dimensions"][1]["choices"][2]["life_paths"].update(
            life_policy="absent"
        ),
        "wrong_account": lambda: data["dimensions"][1]["choices"][2].update(
            life_paths={"cash": "two_premiums"}
        ),
        "wrong_holding": lambda: holding.update(account_id="cash"),
        "no_plan": lambda: data["household"].update(life_plan=None),
    }
    actions[mutation]()


def test_duplicate_dimensions_and_direct_compiler_writes_are_rejected():
    data = case().model_dump(mode="json")
    data["dimensions"].append(dict(data["dimensions"][1], id="conflict"))
    with pytest.raises(ValueError, match="same policy"):
        validate(PolicySearch.model_validate(data))
    choice = case().dimensions[1].choices[0]
    with pytest.raises(ValueError, match="one controlling"):
        selections([choice, choice])
    with pytest.raises(ValueError, match="supplied path"):
        apply(
            case().household.model_dump(mode="json"), case().life_opportunities, {"cash": "missing"}
        )
