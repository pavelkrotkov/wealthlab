"""Original native zero-opening issue and independently retained baseline protection need."""

from wealthlab.optimization.new_life_offers import NewLifeOffer
from wealthlab.products.life_allocation_example import synthetic


def inputs():
    alternatives = synthetic().alternatives
    offer = NewLifeOffer(
        id="supplied_new_issue",
        provenance="illustration",
        owner="person_a",
        holding=alternatives["new_issue"].life_plan.holdings[0],
        matched_new_issue_terms_confirmed=True,
        source="Original complete synthetic zero-opening issue and conditional settlement path",
    )
    return alternatives["no_policy"], [offer]


def offer_changed(configure):
    _, offers = inputs()
    data = offers[0].model_dump(mode="json")
    configure(data)
    return NewLifeOffer.model_validate(data)
