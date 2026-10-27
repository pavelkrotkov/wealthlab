"""Two real product books cannot overwrite the same zero-opening taxable account.

Original capital105000 less actual drilling costs100000 plus residual property
20000 leaves25000 net wealth. The separate QOZ account retains its80000 NAV;
unpaid drilling creditors are already reflected in the remaining55000 liability.
"""

import pytest
from qoz_cases import flat

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.products.drilling_accounts import validate_account as validate_drilling
from wealthlab.products.drilling_example import synthetic as drilling
from wealthlab.products.qoz_accounts import validate_account as validate_qoz


def test_real_qoz_and_drilling_books_preserve_capital_and_reject_shared_ownership():
    data = flat(2026).model_dump(mode="json")
    plan = drilling().model_dump(mode="json")["drilling_plan"]
    plan["observations"] = plan["observations"][:12]
    plan["account_id"] = "qoz"
    data["drilling_plan"] = plan
    shared = Scenario.model_validate(data)
    plan["account_id"] = "drilling"
    data["accounts"].append(dict(data["accounts"][2], id="drilling"))
    separate = Scenario.model_validate(data)
    row = project(separate)[0]
    assert (row["qoz_nav"], row["account_balances"]["qoz"]) == (80000, 80000)
    assert (row["drilling_account_value"], row["drilling_recourse_liability"]) == (0, 55000)
    assert row["net_wealth"] == 25000
    with pytest.raises(ValueError, match="share ownership"):
        validate_qoz(shared, shared.qoz_plan)
    with pytest.raises(ValueError, match="share another product"):
        validate_drilling(shared, shared.drilling_plan)
    with pytest.raises(ValueError, match="share ownership"):
        project(shared)
