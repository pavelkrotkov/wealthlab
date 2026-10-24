"""Reuse the household engine's distinct federal/NJ January-first birthday rule."""

import pytest

from wealthlab.retirement.distribution_example import synthetic
from wealthlab.retirement.distribution_inputs import DistributionCase


def test_tax_forecast_validates_both_jurisdiction_ages():
    data = synthetic().model_dump(mode="json")
    data.update(year=2025, orders=[])
    data["owners"][0]["birth_date"] = "1961-01-01"
    annual = data["annual_tax_case"]
    annual["policy"]["year"] = 2025
    annual["filing"]["age_primary"] = 65
    annual["nj_filing"] = dict(annual["filing"], age_primary=64)
    case = DistributionCase.model_validate(data)
    assert case.annual_tax_case is not None
    assert case.annual_tax_case.nj_filing is not None
    assert case.annual_tax_case.nj_filing.age_primary == 64
    annual["nj_filing"] = None
    with pytest.raises(ValueError, match="federal/NJ ages"):
        DistributionCase.model_validate(data)
