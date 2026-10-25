"""NJ aggregate realization never inherits federal holding-period character."""

import pytest

from tests.option_cases import one_leg, parse
from wealthlab.products.option_engine import run


@pytest.mark.parametrize("physical,expected", [(False, -1500), (True, 4500)])
def test_nj_stock_and_option_rows_have_aggregate_gain_without_federal_character(physical, expected):
    result = run(parse(one_leg(side="short", physical=physical)))
    nj = next(row for row in result["tax"] if row["jurisdiction"] == "nj")
    assert nj["recognized"] == expected
    assert nj["short_term"] is None
    assert nj["long_term"] is None
