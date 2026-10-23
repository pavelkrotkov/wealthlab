"""Quote required cash before optional account sales; contributions use only surplus."""

from decimal import Decimal

from wealthlab.household import debts, flows
from wealthlab.household.calendar import amount


def required(scenario, balances: dict, start, end, fees_owed: Decimal) -> Decimal:
    spending = sum((amount(item, start, end, scenario) for item in scenario.expenses), Decimal(0))
    debt = sum(
        (
            debts.payment(item, balances[item.id], scenario, start, end)[1]
            for item in scenario.debts
        ),
        Decimal(0),
    )
    return spending + debt + flows.fee_due(scenario, start, end) + fees_owed
