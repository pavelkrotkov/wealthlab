"""Original home scenarios use one source capital pool and independently supplied gain facts."""

from wealthlab.household.property_example import synthetic
from wealthlab.household.scenario import Scenario


def change(update):
    data = synthetic().model_dump(mode="json")
    update(data)
    return Scenario.model_validate(data)


def holding(data):
    return data["property_plan"]["holdings"][0]


def sale(data):
    return holding(data)["sale"]


def negative(data):
    sale(data).update(
        gross_proceeds="50000",
        closing_costs="1000",
        maximum_owner_cash_to_close="12000",
        federal_taxable_gain="0",
        nj_taxable_gain="0",
    )


def retain(data):
    holding(data).update(terminal_action="retain", sale=None)
