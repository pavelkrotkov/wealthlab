"""An unsupported product/residence classification is not a zero-tax result."""

import pytest

from wealthlab.tax.spain import evaluate
from wealthlab.tax.spain_example import income, synthetic
from wealthlab.tax.spain_inputs import SpainCase


@pytest.mark.parametrize("product", ["us_retirement", "us_insurance", "us_partnership"])
def test_foreign_wrapper_unknown_blocks_income_and_the_dependent_wealth_cap(product):
    data = synthetic().model_dump(mode="json")
    item = income("foreign", 10000, "unknown")
    item["product"] = product
    data["incomes"].append(item)
    result = evaluate(SpainCase.model_validate(data))
    assert result["income"]["status"] == "blocked"
    assert result["wealth"]["status"] == "blocked"
    assert result["total_liability_eur"] is None
    assert result["full_bilateral_optimization_supported"] is False


def test_unknown_wealth_exemption_preserves_the_independent_income_result():
    data = synthetic().model_dump(mode="json")
    data["assets"][0].update(product="us_retirement", treatment="unknown")
    result = evaluate(SpainCase.model_validate(data))
    assert result["income"]["assessment"]["liability"] == 12787
    assert result["wealth"]["assessment"] is None
    assert result["total_liability_eur"] is None


@pytest.mark.parametrize("treatment", ["deferred", "denied"])
def test_unrecognized_deduction_facts_do_not_reduce_the_current_base(treatment):
    data = synthetic().model_dump(mode="json")
    item = income("unrecognized_loss", -10000, "general")
    item["treatment"] = treatment
    data["incomes"].append(item)
    result = evaluate(SpainCase.model_validate(data))
    assert result["income"]["assessment"]["bases"]["general"] == 50000
    assert result["income"]["assessment"]["liability"] == 12787
