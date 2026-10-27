"""Future PR salaries do not lower current US tax before they are actually earned."""

import pytest
from pr_execution_dated_cases import monthly

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.tax.jurisdiction_execution import evaluate


def test_actual_monthly_w2_only_excludes_earned_source_rows_and_keeps_worldwide_payroll():
    result = evaluate(monthly())
    rows = result["rows"]
    september, final = rows[0]["annual_tax"]["federal"], rows[-1]["annual_tax"]["federal"]
    assert (september["worldwide_gross"], september["taxable_gross"]) == (90000, 60000)
    assert september["standard_deduction"] == 10500
    assert september["employee_payroll"] == 6885
    assert (final["worldwide_gross"], final["pr_excluded_income"]) == (120000, 60000)
    assert final["employee_payroll"] == 9180
    assert rows[0]["income"] == 10000
    assert not rows[-1]["funding_failure"]


def test_unrealized_future_sale_is_not_recognized_and_unsupported_realized_gain_blocks_candidate():
    data = monthly().model_dump(mode="json")
    profile = data["tax_plan"]["cases"][0]["pr_federal"]
    source = dict(
        profile["sources"][0],
        id="future_stock_sale",
        income=dict(
            received="2025-10-31",
            owner="primary",
            kind="long_term",
            federal_amount="10000",
            pr_amount="10000",
            federal_source="US",
            pr_source="US",
            evidence="Synthetic actual stock sale; source/holding clocks not supplied",
        ),
    )
    profile["sources"].append(source)
    early = Scenario.model_validate(dict(data, end="2025-10-01"))
    row = project(early)[-1]
    assert row["annual_tax"]["federal"]["worldwide_gross"] == 90000
    data["tax_plan"]["events"] = [
        dict(
            date="2025-10-31",
            description="Actual stock proceeds25000 less basis15000",
            cash_received="25000",
            federal=dict(long_term="10000"),
            new_jersey=dict(dispositions="10000"),
        )
    ]
    with pytest.raises(ValueError, match="Capital gains require the dated"):
        project(Scenario.model_validate(data))
