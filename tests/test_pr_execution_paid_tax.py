"""PR sees real remaining US paid tax; observing it cannot change the wallet."""

from copy import deepcopy
from decimal import Decimal

import pytest
from pr_execution_helpers import household

from wealthlab.household.projection import project
from wealthlab.tax.pr_execution_paid_tax import evaluate


def test_actual_credit_order_excludes_employee_payroll():
    scenario = household(government=True)
    observed = []
    project(scenario, tax_observer=observed.append)
    position = observed[-1]["closed_returns"][2025]
    result = evaluate(position)
    assert result["federal_foreign_credit"] == Decimal("6724.50")
    assert result["actual_us_income_tax_paid"] == Decimal("6724.50")
    assert result["creditable_us_tax_after_federal_credit"] == Decimal("6724.50")
    assert result["payroll_excluded"] == 7650
    assert result["assessment"]["regular_credit"]["allowed"] == Decimal("6724.50")


def test_observer_copies_do_not_change_other_observations_or_wallet():
    scenario = household(government=True)
    observed = []
    rows = project(scenario, tax_observer=observed.append)
    position = observed[-1]["closed_returns"][2025]
    # An observer only gets detached snapshots, including nested annual facts.
    position.net_paid["federal"] = Decimal(0)
    assert observed[-2]["closed_returns"][2025].net_paid["federal"] > 0
    assert rows == project(scenario)
    assert len(observed) == len(rows) + 1
    assert observed[-1]["phase"] == "terminal"


def test_unpaid_us_income_tax_does_not_generate_pr_credit_and_partial_payment_is_capped():
    observed = []
    project(household(government=True), tax_observer=observed.append)
    position = deepcopy(observed[-1]["closed_returns"][2025])
    # These are actual closed-return positions after initial income-tax cash
    # was refunded; paid employee payroll remains outside the PR credit base.
    position.net_paid["federal"] = Decimal(7650)
    assert evaluate(position)["creditable_us_tax_after_federal_credit"] == 0
    position.net_paid["federal"] += 1000
    assert evaluate(position)["creditable_us_tax_after_federal_credit"] == 1000


def test_unknown_income_payroll_allocation_does_not_create_favorable_paid_tax():
    observed = []
    project(household(government=True), tax_observer=observed.append)
    position = observed[-1]["closed_returns"][2025]
    position.case = position.case.model_copy(
        update=dict(
            payments=position.case.payments.model_copy(update=dict(employee_payroll_withheld=0))
        )
    )
    with pytest.raises(ValueError, match="income/payroll payment allocation"):
        evaluate(position)
