"""Unsupported QuantLib dates and tree inputs produce domain errors rather than app crashes."""

from datetime import date

import pytest

from tests.option_cases import one_leg, parse
from wealthlab.products.option_engine import run
from wealthlab.products.option_valuation import value


@pytest.mark.parametrize("year", [1900, 2200])
def test_out_of_range_model_date_is_a_clear_domain_error(year):
    case = parse(one_leg())
    leg = case.legs[0].model_copy(update=dict(expiry=date(year + 1, 1, 1)))
    mark = case.marks[0].model_copy(update=dict(date=date(year, 1, 1)))
    with pytest.raises(ValueError, match="Unsupported QuantLib valuation"):
        value(leg, mark)


def test_complete_engine_rejects_unsupported_expiry_before_displaying_results():
    data = one_leg()
    data["legs"][0]["expiry"] = "2200-01-01"
    with pytest.raises(ValueError, match="Unsupported QuantLib valuation"):
        run(parse(data))


def test_invalid_american_tree_probability_does_not_escape_as_runtime_error():
    case = parse(one_leg())
    leg = case.legs[0].model_copy(update=dict(style="american"))
    mark = case.marks[0].model_copy(update=dict(rate=1, stock_vol=0.00001))
    with pytest.raises(ValueError, match="Unsupported QuantLib valuation"):
        value(leg, mark)
