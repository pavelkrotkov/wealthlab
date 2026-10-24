"""Preserve positive allocations; independently time supplied federal and NJ negative items.

Loss amounts are assumptions, not generated alpha. The annual tax engine still
applies its capital/NJ category limits after recognition. Eligibility, basis,
at-risk, passive and business-loss determinations are not inferred here.
"""

from decimal import Decimal

from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import TaxEvent


def split(income, negative):
    def part(value):
        return min(value, Decimal(0)) if negative else max(value, Decimal(0))

    data = income.model_dump()
    for key, value in data.items():
        if isinstance(value, Decimal):
            data[key] = part(value)
    if isinstance(income, NJIncome):
        data["business"] = {
            key: part(value) if isinstance(value, Decimal) else value
            for key, value in data["business"].items()
        }
    return type(income).model_validate(data)


def events(item):
    result = [event(item.date, item.id, split(item.federal, False), split(item.new_jersey, False))]
    for jurisdiction, empty in (("federal", FederalIncome()), ("new_jersey", NJIncome())):
        income = split(getattr(item, jurisdiction), True)
        choice = getattr(item, f"{jurisdiction}_loss")
        if income != empty and choice.treatment != "denied":
            validate_choice(item, choice)
            when = choice.release_on or item.date
            values = dict(federal=FederalIncome(), new_jersey=NJIncome())
            values[jurisdiction] = income
            result.append(event(when, f"{item.id}:{jurisdiction}:loss", **values))
    return result


def validate_choice(item, choice):
    if not choice.eligibility_after_limits_assumed:
        raise ValueError(
            "Confirm supplied loss eligibility after applicable limits as an assumption."
        )
    if choice.release_on is not None and choice.release_on <= item.date:
        raise ValueError("Deferred loss release must be later than the original allocation.")


def event(when, description, federal, new_jersey):
    return TaxEvent(
        date=when, description=description, cash_received=0, federal=federal, new_jersey=new_jersey
    )


def audit(item):
    return dict(
        allocation_id=item.id,
        original_date=item.date.isoformat(),
        federal_loss=item.federal_loss.model_dump(mode="json"),
        new_jersey_loss=item.new_jersey_loss.model_dump(mode="json"),
        supplied_negative_federal=split(item.federal, True).model_dump(mode="json"),
        supplied_negative_new_jersey=split(item.new_jersey, True).model_dump(mode="json"),
        recognition_schedule=[e.model_dump(mode="json") for e in events(item)],
        basis_scope="No basis adjustment or legal loss-eligibility calculation",
    )
