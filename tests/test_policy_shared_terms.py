"""A decision menu cannot improve economics by changing its own execution/tax assumptions.

Schedules may add/remove dates and amounts. Costs for the same sale security,
replacement pair and IRA exception status remain shared with the baseline,
including inactive locked alternatives. Different actual source instruments
can still have separately supplied execution terms.
"""

import pytest
from optimization_cases import flat

from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.validation import validate


def menu(field, options):
    data = flat().model_dump(mode="json")
    data["dimensions"] = [
        dict(
            id="policy",
            choices=[dict(id=f"choice_{i}", **{field: orders}) for i, orders in enumerate(options)],
        )
    ]
    return PolicySearch.model_validate(data)


def sale():
    return flat().household.lot_plan.case.sale_policies[0].model_dump(mode="json")


def test_proposed_sale_cannot_lower_the_same_securitys_assumed_commission():
    original = sale()
    case = menu("sale_policies", [[dict(original, commission="0")]])
    with pytest.raises(ValueError, match="shared sale commission"):
        validate(case)


def test_locked_choice_does_not_hide_an_inconsistent_fee_assumption():
    original = sale()
    data = menu("sale_policies", [[original], [dict(original, commission="0")]]).model_dump(
        mode="json"
    )
    data["dimensions"][0]["locked_choice"] = "choice_0"
    with pytest.raises(ValueError, match="shared sale commission"):
        validate(PolicySearch.model_validate(data))


@pytest.mark.parametrize(
    "change", [dict(commission_per_trade="2"), dict(replacement_eligible=False)]
)
def test_same_harvest_pair_preserves_cost_and_replacement_eligibility(change):
    order = dict(
        id="harvest",
        provenance="illustration",
        date="2026-01-31",
        account_id="brokerage",
        security_id="stock",
        replacement_id="replacement",
        replacement_eligible=True,
        prices=dict(stock="100", replacement="100"),
        commission_per_trade="1",
    )
    with pytest.raises(ValueError, match="shared harvest terms"):
        validate(menu("harvest_policies", [[order], [dict(order, **change)]]))


def test_ira_penalty_exception_cannot_be_a_favorable_choice_instead_of_a_shared_fact():
    order = dict(
        id="draw",
        provenance="illustration",
        date="2026-01-01",
        source="ira",
        destination=None,
        kind="withdrawal",
        amount="10000",
        early_penalty_exception=False,
    )
    with pytest.raises(ValueError, match="shared IRA penalty exception"):
        validate(menu("ira_orders", [[order], [dict(order, early_penalty_exception=True)]]))
