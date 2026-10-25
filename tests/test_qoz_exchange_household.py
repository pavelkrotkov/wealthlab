"""Independent products share one real wallet/return and retain every audit/summary."""

from decimal import Decimal

from exchange_fund_cases import flat as exchange
from qoz_cases import flat

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_actual_qoz_and_exchange_ledgers_merge_without_double_counting_capital_or_gains():
    data = flat(2026).model_dump(mode="json")
    other = exchange().model_dump(mode="json")
    data["accounts"].append(other["accounts"][1])
    data["exchange_fund_plan"] = other["exchange_fund_plan"]
    rows = project(Scenario.model_validate(data))
    final = rows[-1]
    assert final["annual_tax"]["federal"]["agi"] == Decimal(160000)
    assert final["annual_tax"]["new_jersey"]["total_income"] == Decimal(140000)
    assert final["qoz_nav"] == final["exchange_locked_value"] == 0
    assert final["qoz_settlement_cash"] == Decimal(80000)
    assert final["qoz_audit"]["calls"][0]["funded"] == Decimal(80000)
    assert final["exchange_fund_audit"]["disposals"]
    assert final["net_wealth"] == Decimal(205000) - final["annual_tax"]["total_liability"]
