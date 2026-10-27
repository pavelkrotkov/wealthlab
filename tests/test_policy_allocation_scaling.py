"""Only explicit monetary fields scale; rates, recognition dates and loss eligibility remain fixed.

Two units cost20000, carry20000initial outside basis, recognize2000supplied
interest and receive a2000independent basis increase. A500unit cash request
becomes1000; native household limit/tax engines act on the resulting totals.
"""

from optimization_allocation_cases import case

from wealthlab.optimization.sleeve_scaling import scale
from wealthlab.products.household_inputs import HouseholdSleeve


def allocated(unit):
    data = unit.model_dump(mode="json")
    data["allocations"] = [
        dict(
            id="income",
            provenance="illustration",
            date="2026-09-01",
            federal=dict(interest="1000", short_term="-500"),
            new_jersey=dict(interest="1000", business=dict(partnership="-500")),
            federal_loss=dict(treatment="denied"),
            new_jersey_loss=dict(treatment="denied"),
        )
    ]
    return data


def test_signed_and_nested_supplied_allocations_scale_without_changing_tax_assumptions():
    data = allocated(case().sleeve_opportunities[0].unit)
    data["case"]["redemptions"] = [
        dict(id="partial", provenance="illustration", date="2026-12-31", amount="500")
    ]
    unit = HouseholdSleeve.model_validate(data)
    scaled = scale(unit, 2)
    item = scaled.allocations[0]
    assert item.federal.interest == item.new_jersey.interest == 2000
    assert item.federal.short_term == item.new_jersey.business.partnership == -1000
    assert item.federal_loss == unit.allocations[0].federal_loss
    assert item.date == unit.allocations[0].date
    assert scaled.case.redemptions[0].amount == 1000


def test_private_outside_basis_changes_and_requests_scale_independently_from_loss_eligibility():
    data = allocated(case().sleeve_opportunities[1].unit)
    contract = data["private_fund_contract"]
    contract["basis_adjustments"] = [
        dict(
            id="basis",
            provenance="illustration",
            date="2026-09-01",
            federal="1000",
            new_jersey="800",
            explanation="Independent supplied federal/NJ adjustments",
        )
    ]
    contract["requests"][0].update(amount="500", complete_liquidation=False)
    unit = HouseholdSleeve.model_validate(data)
    original = fund(unit)
    scaled = fund(scale(unit, 2))
    assert scaled.federal_opening_basis == scaled.new_jersey_opening_basis == 20000
    assert scaled.basis_adjustments[0].federal == 2000
    assert scaled.basis_adjustments[0].new_jersey == 1600
    assert scaled.requests[0].amount == 1000
    assert scaled.requests[0].notice_date == original.requests[0].notice_date
    assert scaled.federal_exit_loss == original.federal_exit_loss


def fund(unit):
    contract = unit.private_fund_contract
    assert contract is not None
    return contract
